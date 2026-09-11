

# MyoBridge

MyoBridge is a real-time surface EMG interface built using a MyoWare 2.0 muscle sensor and an ESP32.

The project captures electrical activity from forearm muscles, processes the EMG signal in software, detects muscle activation, and sends the results to a computer for live visualisation and control.

## Project Goal

Build a simple end-to-end EMG system:

Forearm muscle activity  
↓  
MyoWare 2.0  
↓  
ESP32 ADC  
↓  
Digital signal processing  
↓  
Muscle activation detection  
↓  
Python visualisation / control

## Hardware

- MyoWare 2.0 Muscle Sensor
- MyoWare 2.0 Power Shield
- ESP32 DevKitC
- Surface electrodes
- USB isolator

## Current Status

The MyoWare sensor is powered successfully using the Power Shield.

The RAW output has been measured at approximately 1.9–2.0 V and successfully read by the ESP32 ADC.

The next stage is to acquire a clean RAW EMG signal during muscle contractions before implementing digital rectification and envelope extraction.

## Repository

- `firmware/` — ESP32 firmware
- `python/` — Python recording and visualisation
- `data/` — example EMG recordings

## Planned Pipeline

1. Acquire RAW EMG
2. Sample EMG using ESP32
3. Remove DC offset and rectify signal
4. Extract software envelope
5. Detect muscle activation
6. Visualise EMG in real time
7. Use muscle activation as a control input

## Status

Work in progress.