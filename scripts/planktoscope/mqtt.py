# Library for exchaning messages with Node-RED
# We are using MQTT V3.1.1
# The documentation for Paho can be found here:
# https://www.eclipse.org/paho/clients/python/docs/

# MQTT Topics follows this architecture:
# - actuator :  This topic adresses the stepper control thread
#               No publication under this topic should happen from Python
#   - actuator/pump :   Control of the pump
#                       The message is a json object
#                       {"action":"move", "direction":"FORWARD", "volume":10, "flowrate":1}
#                       to move 10mL forward at 1mL/min
#                       action can be "move" or "stop"
#                       Receive only
#   - actuator/focus :  Control of the focus stage
#                       The message is a json object, speed is optional
#                       {"action":"move", "direction":"UP", "distance":0.26, "speed":1}
#                       to move up 10mm
#                       action can be "move" or "stop"
#                       Receive only
# - imager/image :      This topic adresses the imaging thread
#                       Is a json object with
#                       {"action":"image","sleep":5,"volume":1,"nb_frame":200}
#                       sleep in seconds, volume in mL
#                       Receive only
# - segmenter/segment : This topic adresses the segmenter process
#                       Is a json object with
#                       {"action":"segment"}
#                       Receive only
# - status :    This topics sends feedback to Node-Red
#               No publication or receive at this level
#   - status/pump :     State of the pump
#                       Is a json object with
#                       {"status":"Start", "time_left":25}
#                       Status is one of Started, Ready, Done, Interrupted
#                       Publish only
#   - status/focus :    State of the focus stage
#                       Is a json object with
#                       {"status":"Start", "time_left":25}
#                       Status is one of Started, Ready, Done, Interrupted
#                       Publish only
#   - status/imager :   State of the imager
#                       Is a json object with
#                       {"status":"Start", "time_left":25}
#                       Status is one of Started, Ready, Completed or 12_11_15_0.1.jpg has been imaged.
#                       Publish only
#   - status/segmenter :   Status of the segmentation
#       - status/segmenter/name
#       - status/segmenter/object_id
#       - status/segmenter/metric

# TODO Evaluate the opportunity of saving the last x received messages in a queue for treatment
# We can use collections.deque https://docs.python.org/3/library/collections.html#collections.deque
import paho.mqtt.client as mqtt
import json

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
        self.args = ""
        self.__new_message = False
        self.msg = None

        # MQTT Client functions definition
        self.client = mqtt.Client()
        # self.client.enable_logger(logger)
        self.topic = topic
        self.server = server
        self.port = port
        self.name = name
        self.connect()

    @logger.catch
    def connect(self):
        logger.info(f"trying to connect to {self.server}:{self.port}")
        # TODO add try: except ConnectionRefusedError: block here
        # This is a symptom that Mosquitto may have failed to start
        self.client.connect(self.server, self.port, 60)
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.loop_start()

    ################################################################################
    # MQTT core functions
    ################################################################################

    @logger.catch
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

    @logger.catch
    # Run this function in order to subscribe to all the topics begining by actuator
    def on_subscribe(self, client, obj, mid, granted_qos):
        # Print when subscribed
        # TODO Fix bug when this is called outside of this init function (for example when the imager subscribe to status/pump)
        logger.success(
            f"{self.name} subscribed to {self.topic}! - mid:{str(mid)} qos:{str(granted_qos)}"
        )

    # Run this command when Node-RED is sending a message on the subscribed topic
    @logger.catch
    def on_message(self, client, userdata, msg):
        # Print the topic and the message
        logger.info(f"{self.name}: {msg.topic} {str(msg.qos)} {str(msg.payload)}")
        # Decode the message to find the arguments
        self.args = json.loads(msg.payload.decode())
        logger.debug(f"args are {self.args}")
        self.msg = {"topic": msg.topic, "payload": self.args}
        logger.debug(f"msg is {self.msg}")
        self.__new_message = True

    @logger.catch
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.error(
                f"Connection to the MQTT server is unexpectedly lost by {self.name}"
            )
        else:
            logger.warning(f"Connection to the MQTT server is closed by {self.name}")
        # TODO for now, we just log the disconnection, we need to evaluate what to do
        # in case of communication loss with the server

    def new_message_received(self):
        return self.__new_message

    def read_message(self):
        logger.debug(f"clearing the __new_message flag")
        self.__new_message = False

    @logger.catch
    def shutdown(self, topic="", message=""):
        logger.info(f"Shutting down mqtt client {self.name}")
        self.client.loop_stop()
        logger.debug(f"Mqtt client {self.name} shut down")


# This is called if this script is launched directly
if __name__ == "__main__":
    # TODO This should be a test suite for this library
    pass