The `planktoscope` directory contains the various modules loaded at runtime:

- `imager_state_machine.py` is the state machine class of the imager process.
- `imager.py` is the process that runs the camera
- `light.py` manages the state of the light messages displayed by the Yahboom HAT.
- `mqtt.py` is the class managing the mqtt dialogue with Mosquitto and Node-Red.
- `segmenter.py` is the process that controls the segmentation.
- `stepper.py` is the process that manages the stepper motors and their movements.
