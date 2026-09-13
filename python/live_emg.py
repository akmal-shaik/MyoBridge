import serial
import time
import statistics
import matplotlib.pyplot as plt
import threading
from collections import deque

PORT = "COM6"
BAUD = 115200

WINDOW_SIZE = 100
BASELINE_SAMPLES = 2000
CALIBRATION_SECONDS = 3

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

	envelope = sum(window) / len(window)

	if len(window) == WINDOW_SIZE:
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

	envelope = sum(window) / len(window)

	if len(window) == WINDOW_SIZE:
		flex_values.append(envelope)

flex_level = statistics.quantiles(flex_values, n=100)[89]

signal_range = flex_level - rest_level

flex_threshold = rest_level + 0.35 * signal_range
rest_threshold = rest_level + 0.20 * signal_range

print("\nCalibration complete.")
print(f"Rest level: {rest_level:.1f}")
print(f"Strong flex level: {flex_level:.1f}")
print(f"FLEX threshold: {flex_threshold:.1f}")
print(f"REST threshold: {rest_threshold:.1f}")

# -------------------------
# PREPARE FOR LIVE MODE
# -------------------------

print("\nRELAX your arm...")
print("Live mode starting in 2 seconds.")

# Continuously consume samples instead of sleeping
end_time = time.time() + 2

while time.time() < end_time:
	read_adc()

ser.reset_input_buffer()
window.clear()

state = 0
sample_count = 0

latest_envelope = rest_level
latest_activation = 0
latest_state = "REST"

running = True
lock = threading.Lock()

def process_emg():
	global state
	global sample_count
	global latest_envelope
	global latest_activation
	global latest_state
	global running

	while running:
		adc = read_adc()

		rectified = abs(adc - baseline)
		window.append(rectified)

		envelope = sum(window) / len(window)

		if state == 0 and envelope >= flex_threshold:
			state = 1
		elif state == 1 and envelope <= rest_threshold:
			state = 0

		state_text = "FLEX" if state == 1 else "REST"

		activation_percent = (envelope - rest_level) / (flex_level - rest_level) * 100
		activation_percent = max(0, min(100, activation_percent))

		sample_count += 1

		with lock:
			latest_envelope = envelope
			latest_activation = activation_percent
			latest_state = state_text

processing_thread = threading.Thread(target=process_emg, daemon=True)
processing_thread.start()

display_seconds = 5
display_rate = 20
display_samples = display_seconds * display_rate

time_history = deque(maxlen=display_samples)
envelope_history = deque(maxlen=display_samples)

plt.ion()

fig, ax = plt.subplots(figsize=(11, 5))

line, = ax.plot([], [], linewidth=1.5)

ax.set_title("MyoBridge Live EMG")
ax.set_xlabel("Time (s)")
ax.set_ylabel("EMG envelope (ADC counts)")
ax.grid(True, alpha=0.3)

state_text_display = ax.text(
	0.02,
	0.93,
	"State: REST",
	transform=ax.transAxes,
	fontsize=16
)

activation_text_display = ax.text(
	0.02,
	0.85,
	"Activation: 0%",
	transform=ax.transAxes,
	fontsize=16
)

print("\nLIVE MODE")
print("Close the graph or press Ctrl+C to stop.")

start_time = time.time()

try:
	while plt.fignum_exists(fig.number):
		with lock:
			envelope = latest_envelope
			activation_percent = latest_activation
			state_text = latest_state

		current_time = time.time() - start_time

		time_history.append(current_time)
		envelope_history.append(envelope)

		line.set_data(time_history, envelope_history)

		ax.set_xlim(
			max(0, current_time - display_seconds),
			max(display_seconds, current_time)
		)

		max_envelope = max(
			flex_level * 1.3,
			max(envelope_history, default=flex_level)
		)

		ax.set_ylim(0, max_envelope)

		state_text_display.set_text(
			f"State: {state_text}"
		)

		activation_text_display.set_text(
			f"Activation: {activation_percent:.0f}%"
		)

		fig.canvas.draw_idle()
		fig.canvas.flush_events()

		plt.pause(1 / display_rate)

except KeyboardInterrupt:
	print("\nMyoBridge stopped.")

finally:
	running = False
	processing_thread.join(timeout=1)
	ser.close()
	plt.close("all")