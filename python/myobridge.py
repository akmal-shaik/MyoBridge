import serial
import csv
import time
from pathlib import Path

PORT = "COM6"
BAUD = 115200
SAMPLE_RATE = 1000
DURATION = 20

output_file = Path(__file__).resolve().parents[1] / "data" / "emg_validation.csv"

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
ser.reset_input_buffer()

print(f"Recording EMG for {DURATION} seconds...")

start_time = time.time()
sample_count = 0

with open(output_file, "w", newline="") as file:
	writer = csv.writer(file)
	writer.writerow(["sample", "time_s", "adc"])

	while time.time() - start_time < DURATION:
		line = ser.readline().decode("utf-8", errors="ignore").strip()

		if not line:
			continue

		try:
			adc = int(line)
		except ValueError:
			continue

		time_s = sample_count / SAMPLE_RATE

		writer.writerow([sample_count, time_s, adc])
		sample_count += 1

ser.close()

print(f"Finished. Recorded {sample_count} samples.")
print(f"Saved to: {output_file}")