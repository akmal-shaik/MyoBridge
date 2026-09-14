import serial
import time
import statistics

PORT = "COM6"
BAUD = 115200
SAMPLES = 2000

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
ser.reset_input_buffer()

def read_adc():
	while True:
		line = ser.readline().decode("utf-8", errors="ignore").strip()

		try:
			return int(line)
		except ValueError:
			continue

def collect():
	return [read_adc() for _ in range(SAMPLES)]

print("RELAX completely...")
rest = collect()

baseline = statistics.median(rest)
rest_amplitude = statistics.fmean(abs(x - baseline) for x in rest)

print("Get ready to FLEX...")
for n in [3, 2, 1]:
	print(n)
	time.sleep(1)

ser.reset_input_buffer()

print("FLEX NOW — hold it!")
flex = collect()

flex_amplitude = statistics.fmean(abs(x - baseline) for x in flex)

ser.close()

print()
print(f"Baseline: {baseline:.1f}")
print(f"REST amplitude: {rest_amplitude:.1f}")
print(f"FLEX amplitude: {flex_amplitude:.1f}")
print(f"FLEX/REST ratio: {flex_amplitude / rest_amplitude:.2f}x")

flex_baseline = statistics.median(flex)
flex_centred = statistics.fmean(abs(x - flex_baseline) for x in flex)
print(f"Baseline shift during FLEX: {flex_baseline - baseline:.1f}")
print(f"FLEX amplitude around its own baseline: {flex_centred:.1f}")