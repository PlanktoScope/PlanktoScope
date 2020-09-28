# Our software architecture 

## Node-Red
Node-Red is our main process. We use the flow to manage our user interface through a dashboard instance.


## Python
The python code is separated in four main processes, each with a specific set of responsibilities:

- The main process controls all the others, starts everything up and cleans up on shutdown
- The stepper process manages the stepper movements.
- The imager process controls the camera and the streaming server via a state machine.
- The segmenter process manages the segmentation and its outputs.


Those processes all communicates together using MQTT and json messages. Each message is adressed to one topic. The high level topic controls which process receives the message. The details of each topic is at the end of this commit message. You can learn more about the [MQTT Messages here](mqtt_messages).

The code is architectured around 6 modules and about 10 classes. I encourage you to have a look at the files, they're pretty straightforward to understand.