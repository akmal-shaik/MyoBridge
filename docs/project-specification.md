# MyoBridge Project Specification

## 1. Problem

Traditional computer interfaces rely mainly on keyboards, controllers, touchscreens and cameras. MyoBridge will investigate whether surface electrical activity from forearm muscles can provide a responsive and practical control input.

## 2. Project objective

Design and evaluate a real time system that acquires surface EMG signals, processes them, classifies a small number of hand and wrist gestures, and converts the predictions into external control commands.

## 3. Version 1 demonstration

A user wears one or more surface-EMG sensors on the forearm and performs four classes:

1. Rest
2. Fist
3. Wrist flexion
4. Wrist extension

The system displays the predicted class and confidence in real time. Predictions are then mapped to commands for either a computer application or an existing rover.

## 4. Inputs

* Surface EMG measurements
* Sample timestamps
* Gesture labels during dataset collection
* Session and trial metadata

## 5. Outputs

* Predicted gesture
* Model confidence
* Live signal visualisation
* External control command
* Stored recordings and evaluation results

## 6. Core technical stages

1. EMG signal acquisition
2. Serial data transmission
3. Recording and visualisation
4. Signal filtering
5. Windowing
6. Feature extraction
7. Model training
8. Model evaluation
9. Real time classification
10. External device control

## 7. Core success criteria

Version 1 will be considered complete when:

* EMG recordings can be collected and saved reproducibly.
* At least four gesture classes are represented.
* Data is collected across more than one session.
* At least three classification approaches are compared.
* Evaluation uses trials or sessions not used during training.
* Predictions can run continuously in real time.
* The system controls a digital or physical output.
* Accuracy, latency and limitations are documented.
* Another person can understand the project from the repository.

## 8. Initial performance targets

These targets may be revised after initial experiments.

* Four gesture classes
* At least 80% macro F1 score on an unseen recording session
* End-to-end response below 500 milliseconds
* Stable prediction smoothing
* Safe stop or neutral state when confidence is low

## 9. Current hardware

* ESP32 development board
* Laptop
* Existing components
* Breadboard and jumper wires

## 10. Hardware still required

* Reputable surface-EMG sensor
* Compatible disposable electrodes
* Appropriate battery or isolation arrangement
* A repeatable method of positioning the sensor

## 11. Constraints

* Limited student budget
* Initially tested on one user
* Surface EMG varies with electrode placement and recording session
* Version 1 will use commercial EMG acquisition hardware
* A custom PCB is outside the initial scope

## 12. Version 1 exclusions

The following are explicitly excluded until the core system works:

* EEG
* Medical diagnosis
* Custom analogue EMG amplifier
* Custom PCB
* Robotic prosthetic hand
* Mobile application
* Cloud platform
* Large deep-learning model
* Multi-user clinical study

## 13. Possible future extensions

* Additional EMG channels
* More gesture classes
* Embedded inference on the ESP32
* Wearable enclosure
* Custom acquisition PCB
* Adaptive user calibration
* Electrode-displacement robustness
* Public dataset evaluation
* Rehabilitation or accessibility applications
