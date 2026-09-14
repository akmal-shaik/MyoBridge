import csv
import math
import statistics as st
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import joblib
from sklearn.base import clone

# SETTINGS

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "gestures_train.csv"
OUTPUT_FILE = ROOT / "data" / "gestures_train_features.csv"

WINDOW_SIZE = 200
ZC_THRESHOLD = 5

FEATURE_NAMES = [
	"mav",
	"rms",
	"waveform_length",
	"zero_crossings"
]

EXPECTED_LABELS = {"OPEN_HAND", "FIST", "COMBINED_FLEX"}

# LOAD RECORDING

trials = defaultdict(list)

with INPUT_FILE.open(newline="") as file:
	for row in csv.DictReader(file):
		key = (
			row["session_id"],
			int(row["trial_id"]),
			int(row["repetition"]),
			row["label"]
		)

		adc = int(row["adc"])

		if not 0 <= adc <= 4095:
			raise SystemExit(f"Invalid ADC value: {adc}")

		trials[key].append(adc)

if not trials:
	raise SystemExit("The recording contains no samples.")

labels_found = {key[3] for key in trials}

if labels_found != EXPECTED_LABELS:
	raise SystemExit(f"Expected {EXPECTED_LABELS}, but found {labels_found}.")

repetition_labels = defaultdict(list)

for session_id, trial_id, repetition, label in trials:
	repetition_labels[(session_id, repetition)].append(label)

for group, labels in repetition_labels.items():
	if Counter(labels) != Counter(EXPECTED_LABELS):
		raise SystemExit(f"Repetition {group} needs one trial per gesture.")

if len(repetition_labels) < 2:
	raise SystemExit("At least two repetitions are needed for evaluation.")

# EXTRACT WINDOW FEATURES

features = []

for key, samples in sorted(trials.items()):
	session_id, trial_id, repetition, label = key

	if len(samples) < WINDOW_SIZE:
		raise SystemExit(f"Trial {trial_id} has too few samples.")

	for start in range(0, len(samples) - WINDOW_SIZE + 1, WINDOW_SIZE):
		window = samples[start:start + WINDOW_SIZE]

		baseline = st.fmean(window)
		centred = [x - baseline for x in window]

		mav = st.fmean(abs(x) for x in centred)
		rms = math.sqrt(st.fmean(x * x for x in centred))
		waveform_length = sum(abs(b - a) for a, b in zip(centred, centred[1:]))

		zero_crossings = sum(
			a * b < 0 and abs(b - a) >= ZC_THRESHOLD
			for a, b in zip(centred, centred[1:])
		)

		features.append({
			"session_id": session_id,
			"trial_id": trial_id,
			"repetition": repetition,
			"label": label,
			"window_id": start // WINDOW_SIZE,
			"mav": mav,
			"rms": rms,
			"waveform_length": waveform_length,
			"zero_crossings": zero_crossings
		})

with OUTPUT_FILE.open("w", newline="") as file:
	writer = csv.DictWriter(file, fieldnames=list(features[0]))
	writer.writeheader()
	writer.writerows(features)

print(f"Input: {INPUT_FILE.name}")
print(f"Trials: {len(trials)}")
print(f"Feature windows: {len(features)}")
print(f"Windows per class: {dict(Counter(row['label'] for row in features))}")
print(f"Saved features: {OUTPUT_FILE.name}")

print("\nMedian features per class:")

for label in sorted(EXPECTED_LABELS):
	group = [row for row in features if row["label"] == label]

	summary = ", ".join(
		f"{name}={st.median(row[name] for row in group):.1f}"
		for name in FEATURE_NAMES
	)

	print(f"{label}: {summary}")

# PREPARE MODEL INPUTS

X = np.array([
	[row[name] for name in FEATURE_NAMES]
	for row in features
])

y = np.array([row["label"] for row in features])

groups = np.array([
	f"{row['session_id']}_{row['repetition']}"
	for row in features
])

# EVALUATE HELD-OUT REPETITIONS

rf_predictions = np.empty(len(y), dtype=object)
baseline_predictions = np.empty(len(y), dtype=object)

rf_scores = []

print("\n--- LEAVE-ONE-REPETITION-OUT EVALUATION ---", flush=True)

for train_idx, test_idx in LeaveOneGroupOut().split(X, y, groups):
	# Fresh models for every round
	model = RandomForestClassifier(
		n_estimators=200,
		min_samples_leaf=3,
		random_state=42,
		n_jobs=-1
	)

	baseline = DecisionTreeClassifier(
		max_depth=3,
		min_samples_leaf=3,
		random_state=42
	)

	# Learn only from the training repetitions
	model.fit(X[train_idx], y[train_idx])
	baseline.fit(X[train_idx, :1], y[train_idx])

	# Predict the held out repetition
	predicted = model.predict(X[test_idx])
	simple = baseline.predict(X[test_idx, :1])

	rf_predictions[test_idx] = predicted
	baseline_predictions[test_idx] = simple

	rf_accuracy = accuracy_score(y[test_idx], predicted)
	baseline_accuracy = accuracy_score(y[test_idx], simple)

	rf_scores.append(rf_accuracy)

	repetition = features[test_idx[0]]["repetition"]

	print(
		f"Test repetition {repetition}: "
		f"RF = {rf_accuracy:.1%} | MAV tree = {baseline_accuracy:.1%}",
		flush=True
	)

# RESULTS

print("\n--- OVERALL HELD-OUT RESULTS ---")
print(f"RF accuracy: {accuracy_score(y, rf_predictions):.1%}")
print(f"MAV-tree accuracy: {accuracy_score(y, baseline_predictions):.1%}")
print(f"RF range across repetitions: {min(rf_scores):.1%} to {max(rf_scores):.1%}")

print("\nRandom Forest results per gesture:")

labels = sorted(EXPECTED_LABELS)

print(classification_report(
	y,
	rf_predictions,
	labels=labels,
	digits=3,
	zero_division=0
))

print("Confusion matrix: rows = actual, columns = predicted")
print("Column order:", ", ".join(labels))

matrix = confusion_matrix(y, rf_predictions, labels=labels)

for label, row in zip(labels, matrix):
	print(f"{label:>14}: " + " ".join(f"{count:5d}" for count in row))

print("\nEvaluation complete. Saved models unchanged.")

MODEL_FILE = ROOT / "models" / "emg_random_forest_fist.joblib"
MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

final_model = clone(model)
final_model.fit(X, y)

joblib.dump({
	"model": final_model,
	"feature_names": FEATURE_NAMES,
	"window_size": WINDOW_SIZE,
	"zc_threshold": ZC_THRESHOLD,
	"sample_rate": 1000,
	"training_file": INPUT_FILE.name,
	"training_session_ids": sorted({row["session_id"] for row in features}),
}, MODEL_FILE)

print(f"\nSaved FIST model: {MODEL_FILE}")