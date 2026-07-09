# MyoBridge Engineering Log

## Day 1 — Project definition

### Work completed

* Created the MyoBridge GitHub repository.
* Created the initial repository structure.
* Defined the Version 1 demonstration.
* Defined measurable project success criteria.
* Recorded the initial hardware requirements.
* Identified features that are outside the Version 1 scope.

### Decisions

* Surface EMG will be used before attempting EEG.
* Version 1 will begin with four gesture classes.
* A commercial EMG sensor will be used instead of designing a body-connected amplifier.
* Traditional machine-learning baselines will be tested before complex neural networks.
* The existing rover or a computer interface will be used as the final output.
* A custom PCB will only be considered after the complete prototype works.

### Current risks

* EMG hardware has not yet been selected.
* Signal quality may vary substantially with electrode placement.
* The final number of channels has not yet been decided.
* The achievable real-time accuracy is currently unknown.

### Next action

Build a simulated signal-processing notebook and understand the shape of an EMG classification pipeline before purchasing or connecting hardware.
