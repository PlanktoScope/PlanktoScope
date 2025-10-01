from loguru import logger

import os
import time
import json

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import mqtt
from paho.mqtt.client import Properties
from paho.mqtt.client import PacketTypes

import board
import busio

from adafruit_mcp4725 import MCP4725

# Initialize I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

MCP4725_ADDR = 0x60

# Proportional 0 to 5V
VALUE_MIN = 0
VALUE_MAX = 65535

VOLTAGE_MIN = 0
# if you run it from 3.3V, the output range is 0-3.3V. If you run it from 5V the output range is 0-5V.
VOLTAGE_MAX = 5


def map_to_voltage(value):
    return (value / VALUE_MAX) * VOLTAGE_MAX


def map_to_adc(voltage):
    return int((voltage / VOLTAGE_MAX) * VALUE_MAX)


logger.info("planktoscope.light is loaded")


class Led:
    def __init__(self):
        self.dac = MCP4725(i2c, address=MCP4725_ADDR)
        self.on = False

    def set_voltage(self, vout):
        self.dac.value = map_to_adc(vout)

    def activate_torch(self):
        logger.debug("Activate torch")
        self.set_voltage(5)
        self.on = True

    def deactivate_torch(self):
        logger.debug("Deactivate torch")
        self.set_voltage(0)
        self.on = False

    def save(self):
        logger.debug("Saving DAC value to eeprom")
        self.dac.save_to_eeprom()


################################################################################
# Main Segmenter class
################################################################################
class LightProcess(multiprocessing.Process):
    """This class contains the main definitions for the light of the PlanktoScope"""

    def __init__(self, event, configuration):
        """Initialize the Light class

        Args:
            event (multiprocessing.Event): shutdown event
        """
        super(LightProcess, self).__init__(name="light")

        logger.info("planktoscope.light is initialising")

        self.stop_event = event
        self.light_client = None
        try:
            self.led = Led()
            self.led.deactivate_torch()
        except Exception as e:
            logger.error(
                f"We have encountered an error trying to start the LED module, stopping now, exception is {e}"
            )
            raise e
        else:
            logger.success("planktoscope.light is initialised and ready to go!")

    def led_off(self):
        logger.debug("Turning led off")
        self.led.deactivate_torch()

    def led_on(self):
        logger.debug("Turning led on")
        self.led.activate_torch()

    def publish_status(self):
        self.light_client.client.publish(
            "status/light", json.dumps({"status": "On" if self.led.on else "Off"})
        )

    @logger.catch
    def treat_message(self):
        last_message = None
        last_properties = None
        if self.light_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.light_client.msg["payload"]
            last_properties = self.light_client.msg["properties"]
            logger.debug(last_message)
            self.light_client.read_message()
            if "action" not in last_message and "settings" not in last_message:
                logger.error(f"The received message has the wrong argument {last_message}")
                self.light_client.client.publish(
                    "status/light",
                    '{"status":"Received message did not contain action or settings"}',
                )
                return
        if last_message:
            if "action" in last_message:
                self.process_action(last_message, last_properties)
            elif "settings" in last_message:
                self.process_settings(last_message, last_properties)

    def process_action(self, message, props):
        action = message["action"]
        if action == "on":
            logger.info("Turning the light on.")
            self.led_on()
            self.publish_status()
        elif action == "off":
            logger.info("Turn the light off.")
            self.led_off()
            self.publish_status()
        elif action == "status":
            self.publish_status()
        elif action == "save":
            self.led.save()
        else:
            logger.warning(f"We did not understand the received request {action} - {message}")

        if not hasattr(props, "ResponseTopic"):
            return

        reply_to = props.ResponseTopic

        reply_props = Properties(PacketTypes.PUBLISH)
        if hasattr(props, "CorrelationData"):
            reply_props.CorrelationData = props.CorrelationData

        self.light_client.client.publish(reply_to, json.dumps({}), qos=1, properties=reply_props)

    def process_settings(self, message, properties):
        if "voltage" in message["settings"]:
            voltage = message["settings"]["voltage"]
            self.led.set_voltage(voltage)
            self.light_client.client.publish(
                "status/light", f'{{"status":"Voltage set to {voltage}V"}}'
            )
        else:
            logger.warning(f"We did not understand the received settings request in {message}")
            self.light_client.client.publish(
                "status/light",
                f'{{"status":"Settings request not understood in {message}"}}',
            )

    @logger.catch
    def run(self):
        """This is the function that needs to be started to create a thread"""
        logger.info(f"The light control thread has been started in process {os.getpid()}")

        # MQTT Service connection
        self.light_client = mqtt.MQTT_Client(topic="light", name="light_client")

        # Publish the status "Ready" to via MQTT to Node-RED
        self.light_client.client.publish("status/light", '{"status":"Ready"}')

        logger.success("Light module is READY!")

        # This is the loop
        while not self.stop_event.is_set():
            self.treat_message()
            time.sleep(0.1)

        logger.info("Shutting down the light process")
        self.led.deactivate_torch()
        self.light_client.client.publish("status/light", '{"status":"Dead"}')
        self.light_client.shutdown()
        logger.success("Light process shut down! See you!")
