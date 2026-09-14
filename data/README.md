# MyoBridge recordings

These recordings document the development of a single-channel forearm EMG interface. The final gesture set is OPEN_HAND, FIST and COMBINED_FLEX.

## Main files

| File | Purpose |
|---|---|
| `gestures_train.csv` | Final training recording: five repetitions per gesture, 15 trials |
| `gestures_train_features.csv` | 225 feature windows extracted from the training recording |
| `gestures_validation_01.csv` | First separate recording: 77.8% window accuracy |
| `gestures_validation_02.csv` | Second separate recording: 87.6% window accuracy |
| `gestures_validation_03.csv` | Third separate recording: 93.3% window accuracy |
| `envelope_demo.csv` | Earlier unlabelled recording used by `plot_emg.py` |
| `archive/` | Earlier gesture experiments, initial signal checks and partial recordings |

Each final validation recording contains five repetitions per gesture: 15 trials and 225 complete feature windows.

All three validation recordings were evaluated using the unchanged model trained on `gestures_train.csv`.

Gesture execution was adjusted between validation attempts after inspecting results. These are successive same-day development checks, not independent blinded tests. Retain all three when reporting performance.

## Gesture definitions

| Label | Action |
|---|---|
| `OPEN_HAND` | Open the hand comfortably without forcefully spreading the fingers |
| `FIST` | Comfortable fist, wrist straight, without pressing against a surface |
| `COMBINED_FLEX` | Fist combined with comfortable wrist flexion towards the palm |

The recorder shuffles the gesture order within each repetition. Each trial includes a settling period followed by approximately three seconds of recording.

## Labelled recording columns

| Column | Meaning |
|---|---|
| `session_id` | Identifier for the recording session |
| `trial_id` | Trial number within the session |
| `repetition` | Repetition group containing one trial per gesture |
| `label` | Instructed gesture |
| `sample` | Sample index, restarting for each trial |
| `time_s` | Sample index divided by the nominal 1,000 Hz sampling rate |
| `adc` | Raw 12-bit ESP32 ADC reading |

`time_s` is estimated from sample count; it is not a measured hardware timestamp.

Session IDs remain unchanged when files are renamed. They are used to separate recordings and prevent validation on the training session.

## Feature columns

The feature CSV retains session, trial, repetition and label information and adds:

- `window_id`: non-overlapping window number within the trial.
- `mav`: mean absolute amplitude after removing the window mean.
- `rms`: root mean square of the centred signal.
- `waveform_length`: sum of absolute changes between consecutive samples.
- `zero_crossings`: baseline sign changes with a difference of at least five ADC counts.

Each window contains 200 samples, approximately 200 ms at the nominal sampling rate. Incomplete trailing windows are excluded.

## Earlier experiments

The archive includes three-gesture and four-gesture pilots, partial recordings, original and corrected gesture labels, and palm-down validation attempts.

The PALM_DOWN experiments involved gesture execution that differed from the final FIST definition, including reported desk pressure. They must not be silently relabelled as FIST.

Archived recordings use different schemas and gesture sets. They should not be combined automatically with the final training dataset.

## Interpretation

The final model achieved 88.9% leave-one-repetition-out accuracy on the training recording. A MAV-only decision tree achieved 89.3%.

Separate-recording accuracy ranged from 77.8% to 93.3%. Open-hand/fist confusion and sensitivity to gesture execution remain limitations.

These are unsmoothed window-level scores from one participant on one day. Neighbouring windows are correlated, and performance across users, days and electrode placements is untested.