# MyoBridge

MyoBridge is a real-time EMG gesture-recognition interface using surface electromyography, signal processing, embedded electronics, and machine learning.

The goal is to classify forearm muscle activity and use the recognised gesture to control a digital or physical system.

## Current status

- Simulated EMG signal-processing pipeline completed.
- ESP32 analogue acquisition pipeline completed using a potentiometer test input.
- MyoWare EMG sensor integration pending.

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

