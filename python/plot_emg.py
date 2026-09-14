import csv
import statistics
import matplotlib.pyplot as plt
from pathlib import Path

data_file = Path(__file__).resolve().parents[1] / "data" / "envelope_demo.csv"

time_s = []
adc = []

with open(data_file, "r") as file:
	reader = csv.DictReader(file)

	for row in reader:
		time_s.append(float(row["time_s"]))
		adc.append(int(row["adc"]))

baseline = statistics.median(adc)

centred_adc = [value - baseline for value in adc]
rectified_adc = [abs(value) for value in centred_adc]

window_size = 100
envelope = []

running_sum = 0

for i, value in enumerate(rectified_adc):
	running_sum += value

	if i >= window_size:
		running_sum -= rectified_adc[i - window_size]

	current_window = min(i + 1, window_size)
	envelope.append(running_sum / current_window)

print(f"Estimated baseline: {baseline} ADC counts")

flex_threshold = 25
rest_threshold = 15

activation = []
state = 0

for value in envelope:
	if state == 0 and value >= flex_threshold:
		state = 1
	elif state == 1 and value <= rest_threshold:
		state = 0

	activation.append(state)

rest_values = [value for value, state in zip(envelope, activation) if state == 0]
flex_values = [value for value, state in zip(envelope, activation) if state == 1]

rest_level = statistics.median(rest_values)
flex_level = statistics.quantiles(flex_values, n=100)[94]

activation_percent = []

for value in envelope:
	percent = (value - rest_level) / (flex_level - rest_level) * 100
	percent = max(0, min(100, percent))
	activation_percent.append(percent)

print(f"Rest level: {rest_level:.1f}")
print(f"Strong flex level: {flex_level:.1f}")

plt.figure(figsize=(12, 5))

plt.plot(time_s, envelope, linewidth=1.3, label="Software envelope")
plt.axhline(flex_threshold, linestyle="--", label="FLEX threshold")
plt.axhline(rest_threshold, linestyle="--", label="REST threshold")

plt.title("MyoBridge REST / FLEX Detection")
plt.xlabel("Time (s)")
plt.ylabel("EMG envelope (ADC counts)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()

plt.figure(figsize=(12, 3))

plt.step(time_s, activation, where="post")

plt.title("MyoBridge Detected Muscle State")
plt.xlabel("Time (s)")
plt.ylabel("State")
plt.yticks([0, 1], ["REST", "FLEX"])
plt.ylim(-0.2, 1.2)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()

plt.figure(figsize=(12, 4))

plt.plot(time_s, activation_percent, linewidth=1.3)

plt.title("MyoBridge Muscle Activation Level")
plt.xlabel("Time (s)")
plt.ylabel("Muscle activation (%)")
plt.ylim(-5, 105)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()