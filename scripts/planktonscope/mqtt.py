# Library for exchaning messages with Node-RED
import paho.mqtt.client as mqtt


class MQTT_Client:
    """ A client for MQTT

    Do not forget to include the wildcards in the topic
    when creating this object
    """

    # Declare the global variables command, args and counter
    command = ""
    args = ""
    counter = ""

    def __init__(self, topic, server = "127.0.0.1", port = 1883):
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
    def on_connect(client, userdata, flags, rc):
        # Print when connected
        print("Connected! - " + str(rc))
        # When connected, run subscribe()
        self.client.subscribe(self.topic + "/#")
        # Turn green the light module
        planktonscope.light.setRGB(0, 255, 0)

    # Run this function in order to subscribe to all the topics begining by actuator
    def on_subscribe(client, obj, mid, granted_qos):
        # Print when subscribed
        print("Subscribed! - " + str(mid) + " " + str(granted_qos))

    # Run this command when Node-RED is sending a message on the subscribed topic
    def on_message(client, userdata, msg):
        # Print the topic and the message
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        # Parse the topic to find the command. ex : actuator/pump -> pump
        self.command = msg.topic.split("/")[1]
        # Decode the message to find the arguments
        self.args = str(msg.payload.decode())
        # Reset the counter to 0
        self.counter = 0
