# MyoBridge

A single-channel surface EMG project built with a MyoWare 2.0 sensor, ESP32 and Python. MyoBridge records forearm muscle activity, processes the signal, controls an on-screen paddle and predicts three gestures using a Random Forest classifier.

## Features

- ESP32 acquisition from the MyoWare RAW output at a nominal 1 kHz.
- Baseline removal, rectification and software envelope extraction.
- Calibrated REST/FLEX detection with hysteresis.
- Proportional muscle-controlled paddle with display smoothing.
- Shuffled, labelled gesture recording.
- Four-feature gesture classification and live predictions.
- Evaluation on held-out repetitions and separate same-day recordings.

## Hardware

- MyoWare 2.0 Muscle Sensor
- MyoWare 2.0 Power Shield
- ESP32 DevKitC
- Surface electrodes
- USB isolator

The firmware reads the sensor signal on GPIO34 with 12-bit ADC resolution and streams integer ADC values over serial at 115200 baud.

This is an educational engineering project, not a medical device. Follow the hardware manufacturer's instructions for body-connected use and power isolation.

## Supported gestures

| Label | Action |
|---|---|
| `OPEN_HAND` | Open the hand comfortably without forcefully spreading the fingers |
| `FIST` | Make a comfortable fist with the wrist straight, without pressing against a surface |
| `COMBINED_FLEX` | Make a fist and comfortably bend the wrist towards the palm |

Gesture execution, arm support and electrode placement should remain consistent. The model always chooses one of its supported classes; it does not recognise arbitrary movements as unknown.

Earlier experiments included wrist flexion, wrist extension and a palm-down action. These recordings and earlier models are retained in the archive folders.

## Signal processing

The paddle and gesture classifier use different processing paths:

- **Paddle:** calibrated baseline removal, rectification, a 100-sample moving-average envelope and hysteresis thresholds. Additional smoothing controls paddle position.
- **Classifier:** non-overlapping 200-sample windows, with each window's mean removed before feature extraction.

The classifier uses:

| Feature | Description |
|---|---|
| MAV | Mean absolute amplitude |
| RMS | Root mean square amplitude |
| Waveform length | Sum of absolute differences between consecutive samples |
| Zero crossings | Sign changes around the centred baseline, with a 5-count difference threshold |

At the nominal sampling rate, each classification window represents approximately 200 ms. The zero-crossing threshold is an implementation choice, not a sensor specification.

## Results

The final model recognises `OPEN_HAND`, `FIST` and `COMBINED_FLEX`.

### Held-out repetition evaluation

The training recording contains five repetitions per gesture: 15 trials and 225 feature windows.

Each evaluation round trains on four repetitions and tests on the remaining repetition. All windows from a repetition stay together.

| Model | Window accuracy |
|---|---:|
| Random Forest, four features | 88.9% |
| Small decision tree, MAV only | 89.3% |

The Random Forest uses 200 trees and a minimum leaf size of three. The baseline uses a maximum tree depth of three and a minimum leaf size of three.

The baseline classified one additional window correctly. This experiment does not demonstrate an accuracy advantage for the Random Forest.

After evaluation, the saved Random Forest was trained on all 225 training windows.

### Separate same-day recordings

The saved model was evaluated without retraining on three further recordings. Each contains 15 trials and 225 windows.

| Recording | Window accuracy |
|---|---:|
| `gestures_validation_01.csv` | 77.8% |
| `gestures_validation_02.csv` | 87.6% |
| `gestures_validation_03.csv` | 93.3% |

Gesture execution was adjusted between attempts after inspecting results. These are successive development checks, not independent blinded tests. All three results are retained rather than reporting only the best attempt.

The remaining errors primarily involve confusion between open hand and fist. These scores evaluate unsmoothed window predictions, not the accuracy of the smoothed live display.

## Setup

Install Python and the dependencies from the project root:

```powershell
python -m pip install -r requirements.txt
```

The dependency versions are pinned to those used in the development environment. Saved scikit-learn models should be used with compatible library versions.

For hardware operation:

1. Upload `firmware/myobridge/myobridge.ino` to the ESP32 using the Arduino IDE with ESP32 board support.
2. Set `PORT` in the hardware-facing Python script to the ESP32's serial port. The development setup used `COM6`.
3. Close the Arduino Serial Monitor before running a Python script.

Run only one serial-reading script at a time.

## Run without hardware

Validate the saved model against the configured recording:

```powershell
python .\python\validate_classifier.py
```

The default validation file is `data/gestures_validation_03.csv`. Change `INPUT_FILE` in the script to evaluate another recording.

Plot the saved envelope demonstration:

```powershell
python .\python\plot_emg.py
```

Extract features, evaluate both classifiers and retrain the final model:

```powershell
python -u .\python\emg_ml.py
```

**Training rewrites `data/gestures_train_features.csv` and the saved FIST model. It is not required to run validation or live prediction.**

Validation rejects recordings whose session IDs match the saved model's training-session metadata.

## Run with hardware

Check REST/FLEX signal separation:

```powershell
python .\python\signal_check.py
```

Launch the calibrated signal graph and paddle:

```powershell
python .\python\live_emg.py
```

Record labelled gesture trials:

```powershell
python .\python\myobridge.py
```

Run live gesture classification:

```powershell
python .\python\live_classifier.py
```

The classifier loads `models/emg_random_forest_fist.joblib`.

Its display includes the raw prediction and a three-window majority vote. Smoothing adds delay and can stabilise incorrect predictions; it does not improve the underlying signal. The displayed model score is not a calibrated probability of correctness.

## Repository layout

| Path | Contents |
|---|---|
| `firmware/myobridge/` | ESP32 acquisition firmware |
| `python/` | Recording, processing, training, validation and live demos |
| `data/` | Final training and validation recordings, features and envelope example |
| `data/archive/` | Earlier experiments and partial recordings |
| `models/` | Final FIST-based Random Forest |
| `models/archive/` | Earlier gesture models |
| `requirements.txt` | Python dependencies |

Session IDs remain inside the CSVs even though filenames are descriptive.

## Limitations

- One EMG channel measures activity near one electrode placement; different gestures can produce overlapping signals.
- Predictions depend on contraction effort, gesture execution, contact and arm position.
- Evaluation used one participant and same-day recordings. Generalisation to other users, days and electrode placements is untested.
- Neighbouring windows within a trial are correlated; window counts are not counts of independent recordings.
- CSV time values are derived from a nominal 1 kHz sampling rate rather than hardware timestamps.
- Live processing latency has not been formally benchmarked.
- Calibration percentages describe the session's signal range, not measured muscle force.

## License

MIT — see `LICENSE`.