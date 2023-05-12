################################################################################
# Copyright (C) 2021 Romain Bazile
#
# This file is part of the PlanktoScope software.
#
# PlanktoScope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PlanktoScope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PlanktoScope.  If not, see <http://www.gnu.org/licenses/>.

# Logger library compatible with multiprocessing
from loguru import logger

import os, time

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import planktoscope.mqtt

import planktoscope.i2cscanner

import RPi.GPIO

import subprocess  # nosec

# Library to send command over I2C for the light module on the fan
import smbus2 as smbus

import enum


logger.info("planktoscope.light is loaded")


def i2c_update():
    # Update the I2C Bus in order to really update the LEDs new values
    subprocess.Popen("i2cdetect -y 1".split(), stdout=subprocess.PIPE)  # nosec


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
    DEFAULT_CURRENT = 20

    LED_selectPin = 18

    def __init__(self):
        self.VLED_short = False
        self.thermal_scale = False
        self.thermal_shutdown = False
        self.UVLO = False
        self.flash_timeout = False
        self.IVFM = False
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(self.LED_selectPin, RPi.GPIO.OUT)
        self.output_to_led1()
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
        except Exception as e:
            logger.exception(f"Error with the I2C LED control module, {e}")
            raise
        logger.debug(f"LED module id is {led_id}")
        self.set_torch_current(self.DEFAULT_CURRENT)

    def output_to_led1(self):
        logger.debug("Switching output to LED 1")
        RPi.GPIO.output(self.LED_selectPin, RPi.GPIO.HIGH)

    def output_to_led2(self):
        logger.debug("Switching output to LED 2")
        RPi.GPIO.output(self.LED_selectPin, RPi.GPIO.LOW)

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
        logger.debug(
            f"Setting torch current to {current}mA, or integer {value} in the register"
        )
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

    def on(self):
        logger.debug("Activate torch")
        self._write_byte(self.Register.enable, 0b10)
        self.on = True

    def off(self):
        logger.debug("Deactivate torch")
        self._write_byte(self.Register.enable, 0b00)
        self.off = False

    def _write_byte(self, address, data):
        with smbus.SMBus(1) as bus:
            bus.write_byte_data(self.DEVICE_ADDRESS, address, data)

    def _read_byte(self, address):
        with smbus.SMBus(1) as bus:
            b = bus.read_byte_data(self.DEVICE_ADDRESS, address)
        return b


class direct_led:
    led0Pin = 21
    led1Pin = 22
    led = 0
    powered = False

    def __init__(self):
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(self.led0Pin, RPi.GPIO.OUT)
        RPi.GPIO.output(self.led0Pin, RPi.GPIO.LOW)
        RPi.GPIO.setup(self.led1Pin, RPi.GPIO.OUT)
        RPi.GPIO.output(self.led1Pin, RPi.GPIO.LOW)

    def off(self):
        self.powered = False
        if self.led == 0:
            logger.debug("Turning led 1 off")
            RPi.GPIO.output(self.led0Pin, RPi.GPIO.LOW)
        elif self.led == 1:
            logger.debug("Turning led 2 off")
            RPi.GPIO.output(self.led1Pin, RPi.GPIO.LOW)

    def on(self):
        self.powered = True
        if self.led == 0:
            logger.debug("Turning led 1 on")
            RPi.GPIO.output(self.led0Pin, RPi.GPIO.HIGH)
        elif self.led == 1:
            logger.debug("Turning led 2 on")
            RPi.GPIO.output(self.led1Pin, RPi.GPIO.HIGH)

    def get_state(self):
        return self.on

    def output_to_led1(self):
        logger.debug("Switching output to LED 1")
        if self.powered:
            self.off()
            self.led = 0
            self.on()
        else:
            self.led = 0

    def output_to_led2(self):
        logger.debug("Switching output to LED 2")
        if self.powered:
            self.off()
            self.led = 1
            self.on()
        else:
            self.led = 1

    def set_torch_current(self, current):
        pass


################################################################################
# Main Segmenter class
################################################################################
class LightProcess(multiprocessing.Process):
    """This class contains the main definitions for the light of the PlanktoScope"""

    def __init__(self, event):
        """Initialize the Light class

        Args:
            event (multiprocessing.Event): shutdown event
        """
        super(LightProcess, self).__init__(name="light")

        logger.info("planktoscope.light is initialising")

        self.stop_event = event
        self.light_client = None
        if planktoscope.i2cscanner(0x64):
            try:
                self.led = i2c_led()
                self.led.activate_torch_ramp()
            except Exception as e:
                logger.error(
                    f"We have encountered an error trying to start the LED module, stopping now, exception is {e}"
                )
                self.led.output_to_led2()
                raise e
        else:
            logger.info("No I2C led module found, switching to direct control now")
            self.led = direct_led()
        self.led.on()
        time.sleep(0.5)
        self.led.off()
        self.led.on()
        self.led.output_to_led2()
        time.sleep(0.5)
        self.led.off()
        self.led.output_to_led1()
        logger.success("planktoscope.light is initialised and ready to go!")

    def led_off(self, led):
        if led == 0:
            logger.debug("Turning led 1 off")
        elif led == 1:
            logger.debug("Turning led 2 off")
        self.led.off()

    def led_on(self, led):
        if led not in [0, 1]:
            raise ValueError("Led number is wrong")
        if led == 0:
            logger.debug("Turning led 1 on")
            self.led.output_to_led1()
        elif led == 1:
            logger.debug("Turning led 2 on")
            self.led.output_to_led2()
        self.led.on()

    @logger.catch
    def treat_message(self):
        last_message = None
        if self.light_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.light_client.msg["payload"]
            logger.debug(last_message)
            self.light_client.read_message()
            if "action" not in last_message and "settings" not in last_message:
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.light_client.client.publish(
                    "status/light",
                    '{"status":"Received message did not contain action or settings"}',
                )
                return
        if last_message:
            if "action" in last_message:
                if last_message["action"] == "on":
                    # {"action":"on", "led":"1"}
                    logger.info("Turning the light on.")
                    if "led" not in last_message or last_message["led"] == 1:
                        self.led_on(0)
                        self.light_client.client.publish(
                            "status/light", '{"status":"Led 1: On"}'
                        )
                    elif last_message["led"] == 2:
                        self.led_on(1)
                        self.light_client.client.publish(
                            "status/light", '{"status":"Led 2: On"}'
                        )
                    else:
                        self.light_client.client.publish(
                            "status/light", '{"status":"Error with led number"}'
                        )
                elif last_message["action"] == "off":
                    # {"action":"off", "led":"1"}
                    logger.info("Turn the light off.")
                    if "led" not in last_message or last_message["led"] == 1:
                        self.led_off(0)
                        self.light_client.client.publish(
                            "status/light", '{"status":"Led 1: Off"}'
                        )
                    elif last_message["led"] == 2:
                        self.led_off(1)
                        self.light_client.client.publish(
                            "status/light", '{"status":"Led 2: Off"}'
                        )
                    else:
                        self.light_client.client.publish(
                            "status/light", '{"status":"Error with led number"}'
                        )
                else:
                    logger.warning(
                        f"We did not understand the received request {last_message['action']} - {last_message}"
                    )
            if "settings" in last_message:
                if "current" in last_message["settings"]:
                    if isinstance(self.led, i2c_led):
                        # {"settings":{"current":"20"}}
                        current = last_message["settings"]["current"]
                        led_state = self.led.get_state()
                        logger.info(f"Switching the LED current to {current}mA")
                        if led_state:
                            self.led.off()
                        try:
                            self.led.set_torch_current(current)
                        except Exception:
                            self.light_client.client.publish(
                                "status/light",
                                '{"status":"Error while setting the current"}',
                            )
                        else:
                            self.light_client.client.publish(
                                "status/light",
                                f'{{"status":"Current set to {current}mA"}}',
                            )
                        if led_state:
                            self.led.on()
                    else:
                        self.light_client.client.publish(
                            "status/light",
                            f'{{"status":"Current is not settable on your hardware"}}',
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
        logger.info(
            f"The light control thread has been started in process {os.getpid()}"
        )

        # MQTT Service connection
        self.light_client = planktoscope.mqtt.MQTT_Client(
            topic="light", name="light_client"
        )

        # Publish the status "Ready" to via MQTT to Node-RED
        self.light_client.client.publish("status/light", '{"status":"Ready"}')

        logger.success("Light module is READY!")

        # This is the loop
        while not self.stop_event.is_set():
            self.treat_message()
            time.sleep(0.1)

        logger.info("Shutting down the light process")
        self.led.off()
        if isinstance(self.led, i2c_led):
            self.led.set_torch_current(1)
            self.led.set_flash_current(1)
            self.led.get_flags()

        RPi.GPIO.cleanup()
        self.light_client.client.publish("status/light", '{"status":"Dead"}')
        self.light_client.shutdown()
        logger.success("Light process shut down! See you!")


# This is called if this script is launched directly
if __name__ == "__main__":
    led = i2c_led()
    led.set_torch_current(30)
    led.output_to_led1()
    led.activate_torch_ramp()
    led.on()
    time.sleep(5)
    led.off()
    led.set_torch_current(10)
    led.on()
    time.sleep(5)
    led.off()
    led.set_torch_current(1)
    led.set_flash_current(1)
    led.get_flags()
    RPi.GPIO.cleanup()
