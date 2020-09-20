# Library for exchaning messages with Node-RED
# We are using MQTT V3.1.1
# The documentation for Paho can be found here:
# https://www.eclipse.org/paho/clients/python/docs/

# MQTT Topics follows this architecture:
# - actuator :  This topic adresses the stepper control thread
#               No publication under this topic should happen from Python
#   - actuator/pump :   Control of the pump
#                       The message is something like "FORWARD 10 1"
#                       to move 10mL forward at 1mL/min
#                       Receive only
#   - actuator/focus :  Control of the focus stage
#                       The message is something like "UP 10"
#                       to move up 10mm
#                       Receive only
# - imager/image :      This topic adresses the imaging thread
#                       Receive only
# - status :    This topics sends feedback to Node-Red
#               No publication or receive at this level
#   - status/pump :   State of the pump
#                     Is one of Start, Done, Interrupted
#                     Publish only
#   - status/focus :  State of the focus stage
#                     Is one of Start, Done, Interrupted
#                     Publish only
#   - status/imager : State of the imager
#                     Is one of Start, Completed or 12_11_15_0.1.jpg has been imaged.
#                     Publish only
#   - status/segmentation :   Status of the segmentation
#       - status/segmentation/name
#       - status/segmentation/object_id
#       - status/segmentation/metric

import paho.mqtt.client as mqtt

# Logger library compatible with multiprocessing
from loguru import logger

logger.info("planktoscope.mqtt is loaded")


class MQTT_Client:
    """A client for MQTT

    Do not forget to include the wildcards in the topic
    when creating this object
    """

    def __init__(self, topic, server="127.0.0.1", port=1883, name="client"):

        # Declare the global variables command and args
        self.command = ""
        self.args = ""

        # MQTT Client functions definition
        self.client = mqtt.Client()
        self.topic = topic
        self.server = server
        self.port = port
        self.name = name
        pass

    def connect(self):
        # TODO should we use connect_async here maybe? To defer connection to the server until the call to loop_start()
        self.client.connect(self.server, self.port, 60)
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.loop_start()

    ################################################################################
    # MQTT core functions
    ################################################################################

    # Run this function in order to connect to the client (Node-RED)
    def on_connect(self, client, userdata, flags, rc):
        reason = [
            "0: Connection successful",
            "1: Connection refused - incorrect protocol version",
            "2: Connection refused - invalid client identifier",
            "3: Connection refused - server unavailable",
            "4: Connection refused - bad username or password",
            "5: Connection refused - not authorised",
        ]
        # Print when connected
        logger.success(
            f"{self.name} connected to {self.server}:{self.port}! - {reason[rc]}"
        )
        # When connected, run subscribe()
        self.client.subscribe(self.topic)
        # Turn green the light module
        planktonscope.light.setRGB(0, 255, 0)

    # Run this function in order to subscribe to all the topics begining by actuator
    def on_subscribe(self, client, obj, mid, granted_qos):
        # Print when subscribed
        logger.success(
            f"{self.name} subscribed to {self.topic}! - mid:{str(mid)} qos:{str(granted_qos)}"
        )

    # Run this command when Node-RED is sending a message on the subscribed topic
    def on_message(self, client, userdata, msg):
        # Print the topic and the message
        logger.info(f"{self.name}: {msg.topic} {str(msg.qos)} {str(msg.payload)}")
        # Parse the topic to find the command. ex : actuator/pump -> pump
        # This only removes the top-level topic!
        self.command = msg.topic.split("/", 1)[1]
        # Decode the message to find the arguments
        self.args = str(msg.payload.decode())

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.error(
                f"Connection to the MQTT server is unexpectedly lost by {self.name}"
            )
        else:
            logger.warning(f"Connection to the MQTT server is closed by {self.name}")
        # TODO for now, we just log the disconnection, we need to evaluate what to do
        # in case of communication loss with the server
