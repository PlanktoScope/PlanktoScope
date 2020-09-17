# Library for exchaning messages with Node-RED
# We are using MQTT V3.1.1
# The documentation for Paho can be found here:
# https://www.eclipse.org/paho/clients/python/docs/

# MQTT Topics follows this architecture:
# - actuator :  This topics adresses the actuator thread
#               No publication or receive here
#   - actuator/pump :   Control of the pump
#                       The message should something like "FORWARD 10 1"
#                       to move 10mL forward at 1mL/min
#                       Receive only
#       -actuator/pump/state:   State of the pump
#                               Is one of Start, Done, Interrupted
#                               Publish only
#   - actuator/focus :  Control of the focus stage
#                       The message should something like "UP 10"
#                       to move up 10mm
#                       Receive only
#       -actuator/focus/state   State of the focus stage
#                               Is one of Start, Done, Interrupted
#                               Publish only
#   - imager :  Control of the imaging status
#               Receive only
#       - imager/state :    State of the imager
#                           Is one of Start, Completed or 12_11_15_0.1.jpg has been imaged.
#                           Publish only
# - receiver :  This topics adresses the NODE-RED service
#   - receiver/image :  This does something
#       - receiver/segmentation :   This does something else

import paho.mqtt.client as mqtt


class MQTT_Client:
    """ A client for MQTT

    Do not forget to include the wildcards in the topic
    when creating this object
    """

    # Declare the global variables command, args and counter
    command = ""
    args = ""

    def __init__(self, topic, server="127.0.0.1", port=1883):
        # MQTT Client functions definition
        self.client = mqtt.Client()
        self.topic = topic
        self.server = server
        self.port = port
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
        print("Connected! - " + str(rc))
        # When connected, run subscribe()
        self.client.subscribe(self.topic)
        # Turn green the light module
        planktonscope.light.setRGB(0, 255, 0)

    # Run this function in order to subscribe to all the topics begining by actuator
    def on_subscribe(self, client, obj, mid, granted_qos):
        # Print when subscribed
        print("Subscribed! - " + str(mid) + " " + str(granted_qos))

    # Run this command when Node-RED is sending a message on the subscribed topic
    def on_message(self, client, userdata, msg):
        # Print the topic and the message
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        # Parse the topic to find the command. ex : actuator/pump -> pump
        # This only removes the top-level topic!
        self.command = msg.topic.split("/", 1)[1]
        # Decode the message to find the arguments
        self.args = str(msg.payload.decode())


# TODO implement the on_disconnect callback to manage the loss of the server
# with def on_disconnect(client, userdata, rc)
