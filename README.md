# MyoBridge

MyoBridge is a real time neuromuscular interface that uses surface electromyography, digital signal processing and machine learning to recognise hand gestures and control external devices.

## Project status

**Current phase:** Project definition and signal-acquisition planning.

## Planned system

Forearm muscle activity
        ↓
Surface EMG sensor
        ↓
ESP32 analogue acquisition
        ↓
Filtering and windowing
        ↓
Gesture-classification model
        ↓
Rover or computer control

## Version 1 objective

The first version of MyoBridge will classify a small set of forearm gestures from surface EMG signals and use those predictions to control a digital or physical output in real time.

## Initial gesture classes

* Rest
* Fist
* Wrist flexion
* Wrist extension

## Planned technical areas

* Surface EMG acquisition
* Embedded electronics
* Digital signal processing
* Feature extraction
* Machine-learning classification
* Real-time inference
* Human–machine interfaces

## Project goals

* Build a reproducible EMG data-acquisition pipeline.
* Collect and document a labelled multi-session dataset.
* Compare conventional machine-learning models.
* Evaluate performance on recordings from an unseen session.
* Create a real-time gesture-recognition demonstration.
* Document engineering decisions, failures and limitations.

## Repository structure

```text
docs/       Project specifications and engineering documentation
firmware/   ESP32 acquisition and embedded-inference code
hardware/   Wiring, components and future hardware designs
notebooks/  Signal exploration and model-development notebooks
src/        Reusable Python modules
tests/      Automated tests
results/    Figures, metrics and benchmark results
data/       Dataset documentation and small example files
demo/       Dashboard and demonstration material
```

## Safety

MyoBridge is an educational engineering project and is not a medical device. Only appropriate commercial surface-EMG equipment and safe, isolated or battery-powered configurations will be used for body-connected measurements.

## Roadmap

* [ ] Define Version 1 requirements
* [ ] Build analogue-data streaming pipeline
* [ ] Acquire the first EMG recording
* [ ] Create the preprocessing pipeline
* [ ] Collect a labelled dataset
* [ ] Train baseline classifiers
* [ ] Implement real-time prediction
* [ ] Control an external system
* [ ] Evaluate cross-session performance
* [ ] Publish the technical report and demonstration

