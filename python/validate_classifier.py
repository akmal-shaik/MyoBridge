import csv
import math
import statistics as st
from collections import defaultdict, Counter
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "gestures_validation_03.csv"
MODEL_FILE = ROOT / "models" / "emg_random_forest_fist.joblib"

bundle = joblib.load(MODEL_FILE)
model = bundle["model"]
model.n_jobs = 1

window_size = bundle["window_size"]
zc_threshold = bundle["zc_threshold"]
feature_names = bundle["feature_names"]

trials = defaultdict(list)

with INPUT_FILE.open(newline="") as file:
	for row in csv.DictReader(file):
		key = (row["session_id"], int(row["trial_id"]), row["label"])
		adc = int(row["adc"])

		if not 0 <= adc <= 4095:
			raise SystemExit(f"Invalid ADC value: {adc}")

		trials[key].append(adc)

if not trials:
	raise SystemExit("The recording is empty.")

training_sessions = bundle.get("training_session_ids")

if not training_sessions:
	raise SystemExit("Model needs training-session metadata before validation.")

if any(key[0] in training_sessions for key in trials):
	raise SystemExit("This is the training recording. Use a fresh recording.")

labels = list(model.classes_)
recorded_labels = {key[2] for key in trials}

if recorded_labels != set(labels):
	raise SystemExit(
		f"Label mismatch: model supports {labels}, "
		f"but recording contains {sorted(recorded_labels)}"
	)

X = []
y = []

for (_, trial_id, label), samples in sorted(trials.items()):
	if len(samples) < window_size:
		raise SystemExit(f"Trial {trial_id} has too few samples.")

	for start in range(0, len(samples) - window_size + 1, window_size):
		window = samples[start:start + window_size]
		baseline = st.fmean(window)
		centred = [x - baseline for x in window]

		values = {
			"mav": st.fmean(abs(x) for x in centred),
			"rms": math.sqrt(st.fmean(x * x for x in centred)),
			"waveform_length": sum(abs(b - a) for a, b in zip(centred, centred[1:])),
			"zero_crossings": sum(
				a * b < 0 and abs(b - a) >= zc_threshold
				for a, b in zip(centred, centred[1:])
			)
		}

		X.append([values[name] for name in feature_names])
		y.append(label)

predictions = model.predict(X)

print(f"\nValidation file: {INPUT_FILE.name}")
print(f"Model: {MODEL_FILE.name}")
print(f"Training file: {bundle['training_file']}")
print(f"Trials: {len(trials)}")
print(f"Windows per gesture: {dict(Counter(y))}")
print(f"\nFresh-recording accuracy: {accuracy_score(y, predictions):.1%}")

print(classification_report(
	y,
	predictions,
	labels=labels,
	digits=3,
	zero_division=0
))

print("Confusion matrix: rows = actual, columns = predicted")
print("Column order:", ", ".join(labels))

matrix = confusion_matrix(y, predictions, labels=labels)

for label, row in zip(labels, matrix):
	print(f"{label:>14}: " + " ".join(f"{count:5d}" for count in row))

print("\nValidation complete. No files or models changed.")