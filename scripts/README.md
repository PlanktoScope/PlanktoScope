# Python scripts of the PlanktoScope

This directory contains the various scripts needed for the PlanktoScope to run properly.

You should start your exploration with the file `main.py` as this is the file started by Node-Red.

The `planktoscope` directory contains the various modules loaded at runtime:

- `imager_state_machine.py` is the state machine class of the imager process.
- `imager.py` is the process that runs the camera and the streaming server for the liveview.
- `light.py` manages the state of the light messages displayed by the Yahboom HAT.
- `mqtt.py` is the class managing the mqtt dialogue with Mosquitto and Node-Red.
- `segmenter.py` is the process that controls the segmentation.
- `stepper.py` is the process that manages the stepper motors and their movements.
