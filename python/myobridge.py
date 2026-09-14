import serial
import csv
import time
import random
from pathlib import Path
from datetime import datetime

PORT = "COM6"
BAUD = 115200
SAMPLE_RATE = 1000
DURATION = 3
REPETITIONS = 5

ACTIONS = {
	"OPEN_HAND": "Open your hand comfortably, without pressing against anything.",
	"FIST": "Make a comfortable fist with your wrist straight. Do not press against the desk.",
	"COMBINED_FLEX": "Make a fist and bend your wrist towards your palm comfortably."
}
session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

data_dir = Path(__file__).resolve().parents[1] / "data"
data_dir.mkdir(parents=True, exist_ok=True)

recording_number = 1
output_file = data_dir / f"gestures_recording_{recording_number:02d}.csv"

while output_file.exists():
	recording_number += 1
	output_file = data_dir / f"gestures_recording_{recording_number:02d}.csv"


def read_adc(ser):
	line = ser.readline().decode("utf-8", errors="ignore").strip()

	try:
		adc = int(line)
	except ValueError:
		return None

	return adc if 0 <= adc <= 4095 else None


def drain_for(ser, seconds):
	end_time = time.perf_counter() + seconds

	while time.perf_counter() < end_time:
		ser.readline()


trial_id = 0
total_samples = 0

with serial.Serial(PORT, BAUD, timeout=1) as ser:
	time.sleep(2)
	ser.reset_input_buffer()

	with open(output_file, "x", newline="") as file:
		writer = csv.writer(file)
		writer.writerow([
			"session_id", "trial_id", "repetition",
			"label", "sample", "time_s", "adc"
		])

		try:
			for repetition in range(1, REPETITIONS + 1):
				for label, instruction in random.sample(list(ACTIONS.items()), k=len(ACTIONS)):
					trial_id += 1

					print(f"\nTrial {trial_id}/{REPETITIONS * len(ACTIONS)} — {label}")
					print(instruction)
					input("Press Enter when ready, then begin the action.")

					print("Begin now — settling for 2 seconds...")
					drain_for(ser, 2)
					ser.reset_input_buffer()
					ser.readline()

					print("RECORDING — keep holding the same position.")

					rows = []
					start_time = time.perf_counter()

					while time.perf_counter() - start_time < DURATION:
						adc = read_adc(ser)

						if adc is None:
							continue

						sample = len(rows)
						rows.append([
							session_id, trial_id, repetition,
							label, sample, sample / SAMPLE_RATE, adc
						])

					writer.writerows(rows)
					file.flush()
					total_samples += len(rows)

					print(f"Recorded {len(rows)} samples. RELAX.")
					drain_for(ser, 5)

		except KeyboardInterrupt:
			print("\nStopped early. Completed trials have been saved.")
			raise SystemExit

print(f"\nFinished: {trial_id} trials, {total_samples} samples.")
print(f"Saved to: {output_file}")