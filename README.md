# MyoBridge

MyoBridge is a real-time EMG gesture-recognition interface using surface electromyography, signal processing, embedded electronics, and machine learning.

The goal is to classify forearm muscle activity and use the recognised gesture to control a digital or physical system.

## Current status

Hardware integration update: During initial MyoWare 2.0 integration, the ENV and GND through-hole pads were damaged during soldering, preventing reliable sensor power/output. ESP32 ADC functionality was independently verified. A MyoWare Power Shield has been ordered to bypass the damaged power connections through the sensor's snap interface. The acquisition approach has also been updated to use the RAW EMG output, with rectification and envelope extraction performed digitally in software.

Next: Validate MyoWare operation using Power Shield → acquire real RAW EMG → implement digital rectification and envelope extraction.

## System overview

```text
Forearm muscle activity
        ↓
Surface EMG sensor
        ↓
ESP32 ADC acquisition
        ↓
Python recording pipeline
        ↓
Signal processing and feature extraction
        ↓
Gesture classifier
        ↓
External control output

