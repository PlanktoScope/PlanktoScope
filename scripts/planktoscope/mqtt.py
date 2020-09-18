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
        self.client.connect(self.server, self.port, 60)
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.loop_start()

    ################################################################################
    # MQTT core functions
    ################################################################################

    # Run this function in order to connect to the client (Node-RED)
    def on_connect(self, client, userdata, flags, rc):
        # Print when connected
        print(f"{self.name} connected to {self.server}:{self.port}! - {str(rc)}")
        # When connected, run subscribe()
        self.client.subscribe(self.topic)
        # Turn green the light module
        planktonscope.light.setRGB(0, 255, 0)

    # Run this function in order to subscribe to all the topics begining by actuator
    def on_subscribe(self, client, obj, mid, granted_qos):
        # Print when subscribed
        print(
            f"{self.name} subscribed to {self.topic}! - {str(mid)} {str(granted_qos)}"
        )

    # Run this command when Node-RED is sending a message on the subscribed topic
    def on_message(self, client, userdata, msg):
        # Print the topic and the message
        print(f"{self.name}: {msg.topic} {str(msg.qos)} {str(msg.payload)}")
        # Parse the topic to find the command. ex : actuator/pump -> pump
        # This only removes the top-level topic!
        self.command = msg.topic.split("/", 1)[1]
        # Decode the message to find the arguments
        self.args = str(msg.payload.decode())


# TODO implement the on_disconnect callback to manage the loss of the server
# with def on_disconnect(client, userdata, rc)
