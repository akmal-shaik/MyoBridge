from __future__ import annotations

import csv
import time
from pathlib import Path

import serial


SERIAL_PORT = "COM6"
BAUD_RATE = 115200
RECORDING_DURATION_SECONDS = 10

OUTPUT_PATH = Path("data/sample/esp32_analog_test.csv")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        connection = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=1,
        )
    except serial.SerialException as error:
        raise SystemExit(f"Could not open {SERIAL_PORT}: {error}") from error

    time.sleep(2)

    start_time = time.time()
    rows_written = 0

    try:
        with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp_us", "adc_value"])

            while time.time() - start_time < RECORDING_DURATION_SECONDS:
                line = connection.readline().decode("utf-8", errors="ignore").strip()

                if not line or line.startswith("timestamp"):
                    continue

                parts = line.split(",")

                if len(parts) != 2:
                    continue

                timestamp_text, adc_text = parts

                try:
                    timestamp_us = int(timestamp_text)
                    adc_value = int(adc_text)
                except ValueError:
                    continue

                writer.writerow([timestamp_us, adc_value])
                rows_written += 1

    finally:
        connection.close()

    print(f"Saved {rows_written} samples to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()