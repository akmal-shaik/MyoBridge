import serial
import time
import statistics
import threading
import matplotlib.pyplot as plt

from collections import deque
from matplotlib.animation import FuncAnimation

PORT = "COM6"
BAUD = 115200

WINDOW_SIZE = 100
BASELINE_SAMPLES = 2000
CALIBRATION_SECONDS = 3
MIN_SIGNAL_RANGE = 15

ser = serial.Serial(PORT, BAUD, timeout=1)

time.sleep(2)
ser.reset_input_buffer()

def read_adc():
	while True:
		line = ser.readline().decode("utf-8", errors="ignore").strip()

		if not line:
			continue

		try:
			return int(line)
		except ValueError:
			continue


# -------------------------
# BASELINE
# -------------------------

print("MyoBridge calibration")
print("Keep your arm RELAXED...")

baseline_samples = []

while len(baseline_samples) < BASELINE_SAMPLES:
	baseline_samples.append(read_adc())

baseline = statistics.median(baseline_samples)

print(f"Baseline: {baseline:.1f} ADC counts")


# -------------------------
# REST CALIBRATION
# -------------------------

window = deque(maxlen=WINDOW_SIZE)

print("\nMeasuring REST level for 3 seconds...")

rest_values = []
end_time = time.time() + CALIBRATION_SECONDS

while time.time() < end_time:
	adc = read_adc()

	rectified = abs(adc - baseline)
	window.append(rectified)

	if len(window) == WINDOW_SIZE:
		envelope = sum(window) / WINDOW_SIZE
		rest_values.append(envelope)

rest_level = statistics.median(rest_values)

print(f"Rest level: {rest_level:.1f}")


# -------------------------
# FLEX CALIBRATION
# -------------------------

print("\nGet ready to FLEX strongly...")

for number in [3, 2, 1]:
	print(number)
	time.sleep(1)

ser.reset_input_buffer()
window.clear()

print("FLEX NOW!")

flex_values = []
end_time = time.time() + CALIBRATION_SECONDS

while time.time() < end_time:
	adc = read_adc()

	rectified = abs(adc - baseline)
	window.append(rectified)

	if len(window) == WINDOW_SIZE:
		envelope = sum(window) / WINDOW_SIZE
		flex_values.append(envelope)

flex_level = statistics.quantiles(flex_values, n=100)[89]

signal_range = flex_level - rest_level

print("\nCalibration complete.")
print(f"Rest level: {rest_level:.1f}")
print(f"Strong flex level: {flex_level:.1f}")


# -------------------------
# CALIBRATION CHECK
# -------------------------

if signal_range < MIN_SIGNAL_RANGE:
	print("\nCALIBRATION FAILED")
	print("The FLEX signal is not sufficiently different from REST.")
	print("Check electrode placement/contact and run the program again.")

	ser.close()
	raise SystemExit


# -------------------------
# THRESHOLDS
# -------------------------

flex_threshold = rest_level + 0.35 * signal_range
rest_threshold = rest_level + 0.20 * signal_range

print(f"FLEX threshold: {flex_threshold:.1f}")
print(f"REST threshold: {rest_threshold:.1f}")


# -------------------------
# PREPARE LIVE MODE
# -------------------------

print("\nRELAX your arm...")
print("Live mode starting in 2 seconds.")

end_time = time.time() + 2

while time.time() < end_time:
	read_adc()

ser.reset_input_buffer()
window.clear()


# -------------------------
# LIVE PROCESSING THREAD
# -------------------------

state = 0

latest_envelope = rest_level
latest_activation = 0.0
latest_state = "REST"

running = True
lock = threading.Lock()


def process_emg():
	global state
	global latest_envelope
	global latest_activation
	global latest_state
	global running

	while running:
		adc = read_adc()

		rectified = abs(adc - baseline)
		window.append(rectified)

		if len(window) < WINDOW_SIZE:
			continue

		envelope = sum(window) / WINDOW_SIZE

		if state == 0 and envelope >= flex_threshold:
			state = 1
		elif state == 1 and envelope <= rest_threshold:
			state = 0

		state_text = "FLEX" if state == 1 else "REST"

		activation_percent = (envelope - rest_level) / signal_range * 100
		activation_percent = max(0, min(100, activation_percent))

		with lock:
			latest_envelope = envelope
			latest_activation = activation_percent
			latest_state = state_text


processing_thread = threading.Thread(
	target=process_emg,
	daemon=True
)

processing_thread.start()


# -------------------------
# DASHBOARD
# -------------------------

# -------------------------
# DASHBOARD + PADDLE DEMO
# -------------------------

DISPLAY_SECONDS = 5
DISPLAY_RATE = 20
DISPLAY_SAMPLES = DISPLAY_SECONDS * DISPLAY_RATE

time_history = deque(maxlen=DISPLAY_SAMPLES)
envelope_history = deque(maxlen=DISPLAY_SAMPLES)

fig, (ax, control_ax) = plt.subplots(
	1, 2,
	figsize=(12, 5),
	gridspec_kw={"width_ratios": [3, 1]},
	constrained_layout=True
)

line, = ax.plot([], [], linewidth=1.5)

ax.set_title("MyoBridge Live EMG")
ax.set_xlabel("Time (s)")
ax.set_ylabel("EMG envelope (ADC counts)")
ax.grid(True, alpha=0.3)

state_display = ax.text(
	0.02, 0.93, "State: REST",
	transform=ax.transAxes,
	fontsize=16
)

activation_display = ax.text(
	0.02, 0.85, "Activation: 0%",
	transform=ax.transAxes,
	fontsize=16
)

control_ax.set_title("Move into the green zone")
control_ax.set_xlim(0, 1)
control_ax.set_ylim(-5, 105)
control_ax.set_xticks([])
control_ax.set_yticks([0, 20, 40, 60, 80, 100])
control_ax.set_ylabel("Calibrated activation (%)")
control_ax.grid(True, axis="y", alpha=0.3)

control_ax.axhspan(60, 80, color="limegreen", alpha=0.2)

paddle = control_ax.axhline(
	0,
	xmin=0.20,
	xmax=0.80,
	color="royalblue",
	linewidth=10
)

target_display = control_ax.text(
	0.5, 0.70, "TARGET",
	transform=control_ax.transAxes,
	ha="center",
	va="center",
	fontweight="bold"
)

start_time = time.time()

paddle_activation = 0.0

def update_dashboard(frame):
	global paddle_activation
	with lock:
		envelope = latest_envelope
		activation = latest_activation
		state_text = latest_state

	current_time = time.time() - start_time

	time_history.append(current_time)
	envelope_history.append(envelope)

	line.set_data(list(time_history), list(envelope_history))

	ax.set_xlim(
		max(0, current_time - DISPLAY_SECONDS),
		max(DISPLAY_SECONDS, current_time)
	)

	y_max = max(
		flex_level * 1.3,
		max(envelope_history, default=flex_level) * 1.1
	)

	ax.set_ylim(0, y_max)

	state_display.set_text(f"State: {state_text}")
	activation_display.set_text(f"Activation: {activation:.0f}%")

	paddle_activation += 0.15 * (activation - paddle_activation)
	paddle.set_ydata([paddle_activation, paddle_activation])

	in_target = 60 <= paddle_activation <= 80
	paddle.set_color("forestgreen" if in_target else "royalblue")
	target_display.set_text("HOLD HERE" if in_target else "TARGET")

	return line, state_display, activation_display, paddle, target_display


animation = FuncAnimation(
	fig,
	update_dashboard,
	interval=1000 / DISPLAY_RATE,
	cache_frame_data=False
)

print("\nLIVE MODE")
print("Control the paddle with your muscle.")
print("Aim for the green zone between 60% and 80%.")
print("Close the graph to stop.")

try:
	plt.show()

except KeyboardInterrupt:
	pass

finally:
	running = False
	processing_thread.join(timeout=1)
	ser.close()
	plt.close("all")
	print("MyoBridge stopped.")