import time
import math
import statistics as st
from pathlib import Path

import serial
import joblib

from collections import deque, Counter

ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = ROOT / "models" / "emg_random_forest_fist.joblib"

PORT = "COM6"
BAUD = 115200

bundle = joblib.load(MODEL_FILE)
model = bundle["model"]
model.n_jobs = 1

WINDOW_SIZE = bundle["window_size"]
ZC_THRESHOLD = bundle["zc_threshold"]
FEATURE_NAMES = bundle["feature_names"]


def extract_features(samples):
	baseline = st.fmean(samples)
	centred = [x - baseline for x in samples]

	values = {
		"mav": st.fmean(abs(x) for x in centred),
		"rms": math.sqrt(st.fmean(x * x for x in centred)),
		"waveform_length": sum(abs(b - a) for a, b in zip(centred, centred[1:])),
		"zero_crossings": sum(
			a * b < 0 and abs(b - a) >= ZC_THRESHOLD
			for a, b in zip(centred, centred[1:])
		)
	}

	return [values[name] for name in FEATURE_NAMES]


print("MyoBridge live gesture classifier")
print("Gestures:", ", ".join(model.classes_))
print("Press Ctrl+C to stop.")

try:
	with serial.Serial(PORT, BAUD, timeout=1) as ser:
		time.sleep(2)
		ser.reset_input_buffer()
		ser.readline()

		window = []
		prediction_history = deque(maxlen=3)
		last_sample_time = time.perf_counter()

		while True:
			line = ser.readline().decode("utf-8", errors="ignore").strip()

			try:
				adc = int(line)
			except ValueError:
				if time.perf_counter() - last_sample_time > 3:
					print("\nNo valid samples: check the ESP32 connection.")
					last_sample_time = time.perf_counter()
					window.clear()
				continue

			if not 0 <= adc <= 4095:
				continue

			last_sample_time = time.perf_counter()
			window.append(adc)

			if len(window) < WINDOW_SIZE:
				continue

			features = extract_features(window)
			probabilities = model.predict_proba([features])[0]

			best_index = probabilities.argmax()
			gesture = model.classes_[best_index]
			score = probabilities[best_index]

			prediction_history.append(gesture)

			if len(prediction_history) < 3:
				stable_gesture = "WAITING"
			else:
				winner, votes = Counter(prediction_history).most_common(1)[0]
				stable_gesture = winner if votes >= 2 else "UNCERTAIN"

			print(
				f"\rRaw: {gesture:<15} | "
				f"Smoothed: {stable_gesture:<15} | "
				f"Raw score: {score:5.1%}   ",
				end="",
				flush=True
			)

			window.clear()

except KeyboardInterrupt:
	print("\nClassifier stopped.")