################################################################################
# Practical Libraries
################################################################################
# Logger library compatible with multiprocessing
from loguru import logger

from gpiozero import DigitalOutputDevice

import os
import time
import json

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import mqtt

# Library to send command over I2C for the light module
import smbus2 as smbus

import enum

logger.info("planktoscope.light is loaded")


class i2c_led:
    """
    LM36011 Led controller
    """

    @enum.unique
    class Register(enum.IntEnum):
        enable = 0x01
        configuration = 0x02
        flash = 0x03
        torch = 0x04
        flags = 0x05
        id_reset = 0x06

    DEVICE_ADDRESS = 0x64
    # This constant defines the current (mA) sent to the LED, 10 allows the use of the full ISO scale and results in a voltage of 2.77v
    DEFAULT_CURRENT = 10

    def __init__(self, configuration):
        hat_type = configuration.get("hat_type") or ""
        hat_version = float(configuration.get("hat_version") or 0)

        # The led is controlled by LM36011
        # but on version 1.2 of the PlanktoScope HAT (PlanktoScope v2.6)
        # the circuit is connected to the pin 18 so it needs to be high
        # pin is assigned to self to prevent gpiozero from immediately releasing it
        if hat_type != "planktoscope" or hat_version < 3.2:
            self.__pin = DigitalOutputDevice(pin=18, initial_value=True)

        self.VLED_short = False
        self.thermal_scale = False
        self.thermal_shutdown = False
        self.UVLO = False
        self.flash_timeout = False
        self.IVFM = False
        self.on = False
        try:
            self.force_reset()
            if self.get_flags():
                logger.error("Flags raised in the LED Module, clearing now")
                self.VLED_short = False
                self.thermal_scale = False
                self.thermal_shutdown = False
                self.UVLO = False
                self.flash_timeout = False
                self.IVFM = False
            led_id = self.get_id()
        except (OSError, Exception) as e:
            logger.exception(f"Error with the LED control module, {e}")
            raise
        logger.debug(f"LED module id is {led_id}")

    def get_id(self):
        led_id = self._read_byte(self.Register.id_reset)
        led_id = led_id & 0b111111
        return led_id

    def get_state(self):
        return self.on

    def activate_torch_ramp(self):
        logger.debug("Activating the torch ramp")
        reg = self._read_byte(self.Register.configuration)
        reg = reg | 0b1
        self._write_byte(self.Register.configuration, reg)

    def deactivate_torch_ramp(self):
        logger.debug("Deactivating the torch ramp")
        reg = self._read_byte(self.Register.configuration)
        reg = reg | 0b0
        self._write_byte(self.Register.configuration, reg)

    def force_reset(self):
        logger.debug("Resetting the LED chip")
        self._write_byte(self.Register.id_reset, 0b10000000)

    def get_flags(self):
        flags = self._read_byte(self.Register.flags)
        self.flash_timeout = bool(flags & 0b1)
        self.UVLO = bool(flags & 0b10)
        self.thermal_shutdown = bool(flags & 0b100)
        self.thermal_scale = bool(flags & 0b1000)
        self.VLED_short = bool(flags & 0b100000)
        self.IVFM = bool(flags & 0b1000000)
        if self.VLED_short:
            logger.warning("Flag VLED_Short asserted")
        if self.thermal_scale:
            logger.warning("Flag thermal_scale asserted")
        if self.thermal_shutdown:
            logger.warning("Flag thermal_shutdown asserted")
        if self.UVLO:
            logger.warning("Flag UVLO asserted")
        if self.flash_timeout:
            logger.warning("Flag flash_timeout asserted")
        if self.IVFM:
            logger.warning("Flag IVFM asserted")
        return flags

    def set_torch_current(self, current):
        # From 3 to 376mA
        # Curve is not linear for some reason, but this is close enough
        if current > 376:
            raise ValueError("the chosen current is too high, max value is 376mA")
        value = int(current * 0.34)
        logger.debug(f"Setting torch current to {current}mA, or integer {value} in the register")
        try:
            self._write_byte(self.Register.torch, value)
        except Exception as e:
            logger.exception(f"Error with the LED control module, {e}")
            raise

    def set_flash_current(self, current):
        # From 11 to 1500mA
        # Curve is not linear for some reason, but this is close enough
        value = int(current * 0.085)
        logger.debug(f"Setting flash current to {value}")
        self._write_byte(self.Register.flash, value)

    def activate_torch(self):
        logger.debug("Activate torch")
        self._write_byte(self.Register.enable, 0b10)
        self.on = True

    def deactivate_torch(self):
        logger.debug("Deactivate torch")
        self._write_byte(self.Register.enable, 0b00)
        self.on = False

    def _write_byte(self, address, data):
        with smbus.SMBus(1) as bus:
            bus.write_byte_data(self.DEVICE_ADDRESS, address, data)

    def _read_byte(self, address):
        with smbus.SMBus(1) as bus:
            b = bus.read_byte_data(self.DEVICE_ADDRESS, address)
        return b


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
            self.led = i2c_led(configuration)
            self.led.set_torch_current(self.led.DEFAULT_CURRENT)
            self.led.activate_torch_ramp()
            self.led.activate_torch()
            time.sleep(0.5)
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
        if self.light_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.light_client.msg["payload"]
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
                action = last_message["action"]
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
                else:
                    logger.warning(
                        f"We did not understand the received request {action} - {last_message}"
                    )
            if "settings" in last_message:
                if "current" in last_message["settings"]:
                    # {"settings":{"current":"20"}}
                    current = last_message["settings"]["current"]
                    if self.led.get_state():
                        # Led is on, rejecting the change
                        self.light_client.client.publish(
                            "status/light",
                            '{"status":"Turn off the LED before changing the current"}',
                        )
                        return
                    logger.info(f"Switching the LED current to {current}mA")
                    try:
                        self.led.set_torch_current(current)
                    except Exception:
                        self.light_client.client.publish(
                            "status/light",
                            '{"status":"Error while setting the current, power cycle your machine"}',
                        )
                    else:
                        self.light_client.client.publish(
                            "status/light", f'{{"status":"Current set to {current}mA"}}'
                        )
                else:
                    logger.warning(
                        f"We did not understand the received settings request in {last_message}"
                    )
                    self.light_client.client.publish(
                        "status/light",
                        f'{{"status":"Settings request not understood in {last_message}"}}',
                    )

    ################################################################################
    # While loop for capturing commands from Node-RED
    ################################################################################
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
        self.led.set_torch_current(1)
        self.led.set_flash_current(1)
        self.led.get_flags()
        self.light_client.client.publish("status/light", '{"status":"Dead"}')
        self.light_client.shutdown()
        logger.success("Light process shut down! See you!")
