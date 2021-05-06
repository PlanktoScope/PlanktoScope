################################################################################
# Practical Libraries
################################################################################
# Logger library compatible with multiprocessing
from loguru import logger

import os, time

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import planktoscope.mqtt

import RPi.GPIO

import subprocess  # nosec

# Library to send command over I2C for the light module on the fan
try:
    import smbus2 as smbus
except ModuleNotFoundError:  # We need this to install the library on machine that do not have the module yet
    subprocess.run("pip3 install smbus2".split())  # nosec
    import smbus2 as smbus

import enum


@enum.unique
class Register(enum.IntEnum):
    enable = 0x01
    configuration = 0x02
    flash = 0x03
    torch = 0x04
    flags = 0x05
    id_reset = 0x06


DEVICE_ADDRESS = 0x64

led_selectPin = 18

logger.info("planktoscope.light is loaded")


def i2c_update():
    # Update the I2C Bus in order to really update the LEDs new values
    subprocess.Popen("i2cdetect -y 1".split(), stdout=subprocess.PIPE)  # nosec


class i2c_led:
    """
    LM36011 Led controller
    """

    def __init__(self):
        self.VLED_short = False
        self.thermal_scale = False
        self.thermal_shutdown = False
        self.UVLO = False
        self.flash_timeout = False
        self.IVFM = False
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(led_selectPin, RPi.GPIO.OUT)
        RPi.GPIO.output(led_selectPin, RPi.GPIO.HIGH)
        try:
            led_id = self.get_id()
        except Exception as e:
            logger.exception(f"Error with the LED control module, {e}")
            raise e
        logger.debug(f"LED module id is {led_id}")

    def output_to_led1(self):
        logger.debug("Switching output to LED 1")
        RPi.GPIO.output(led_selectPin, RPi.GPIO.HIGH)

    def output_to_led2(self):
        logger.debug("Switching output to LED 2")
        RPi.GPIO.output(led_selectPin, RPi.GPIO.LOW)

    def get_id(self):
        led_id = self._read_byte(Register.id_reset)
        led_id = led_id & 0b111111
        logger.debug(f"LED device ID is {led_id}")
        return led_id

    def activate_torch_ramp(self):
        logger.debug("Activating the torch ramp")
        reg = self._read_byte(Register.configuration)
        reg = reg | 0b1
        self._write_byte(Register.configuration, reg)

    def deactivate_torch_ramp(self):
        logger.debug("Deactivating the torch ramp")
        reg = self._read_byte(Register.configuration)
        reg = reg | 0b0
        self._write_byte(Register.configuration, reg)

    def get_flags(self):
        flags = self._read_byte(Register.flags)
        self.flash_timeout = bool(flags & 0b1)
        self.UVLO = bool(flags & 0b10)
        self.thermal_shutdown = bool(flags & 0b100)
        self.thermal_scale = bool(flags & 0b1000)
        self.VLED_short = bool(flags & 0b100000)
        self.IVFM = bool(flags & 0b1000000)

    def set_torch_current(self, current):
        # From 3 to 376mA
        # Curve is not linear for some reason, but this is close enough
        value = int(current * 0.34)
        logger.debug(f"Setting torch current to {value}")
        self._write_byte(Register.torch, value)

    def set_flash_current(self, current):
        # From 11 to 1500mA
        # Curve is not linear for some reason, but this is close enough
        value = int(current * 0.085)
        logger.debug(f"Setting flash current to {value}")
        self._write_byte(Register.flash, value)

    def activate_torch(self):
        logger.debug("Activate torch current")
        self._write_byte(Register.enable, 0b10)

    def deactivate_torch(self):
        logger.debug("Deactivate torch current")
        self._write_byte(Register.enable, 0b00)

    def _write_byte(self, address, data):
        with smbus.SMBus(1) as bus:
            bus.write_byte_data(DEVICE_ADDRESS, address, data)

    def _read_byte(self, address):
        with smbus.SMBus(1) as bus:
            b = bus.read_byte_data(DEVICE_ADDRESS, address)
        return b


class pwm_led:
    def __init__(self, led):
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        self.led = led
        if self.led == 0:
            RPi.GPIO.setup(led0Pin, RPi.GPIO.OUT)
            RPi.GPIO.output(led0Pin, RPi.GPIO.LOW)
            self.pwm0 = RPi.GPIO.PWM(led0Pin, FREQUENCY)
            self.pwm0.start(0)
        elif self.led == 1:
            RPi.GPIO.setup(led1Pin, RPi.GPIO.OUT)
            RPi.GPIO.output(led1Pin, RPi.GPIO.LOW)
            self.pwm1 = RPi.GPIO.PWM(led1Pin, FREQUENCY)
            self.pwm1.start(0)

    def change_duty(self, dc):
        if self.led == 0:
            self.pwm0.ChangeDutyCycle(dc)
        elif self.led == 1:
            self.pwm1.ChangeDutyCycle(dc)

    def off(self):
        if self.led == 0:
            logger.debug("Turning led 1 off")
            self.pwm0.ChangeDutyCycle(0)
        elif self.led == 1:
            logger.debug("Turning led 2 off")
            self.pwm1.ChangeDutyCycle(0)

    def on(self):
        if self.led == 0:
            logger.debug("Turning led 1 on")
            self.pwm0.ChangeDutyCycle(100)
        elif self.led == 1:
            logger.debug("Turning led 2 on")
            self.pwm1.ChangeDutyCycle(100)

    def stop(self):
        if self.led == 0:
            self.pwm0.stop()
        elif self.led == 1:
            self.pwm1.stop()


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
        try:
            self.led = i2c_led()
        except Exception as e:
            logger.error(
                "We have encountered an error trying to start the LED module, stopping now"
            )
            raise e
        self.led.set_torch_current(10)
        self.led.output_to_led1()
        self.led.activate_torch_ramp()
        self.led.activate_torch()
        time.sleep(1)
        self.led.deactivate_torch()

        logger.success("planktoscope.light is initialised and ready to go!")

    def led_off(self, led):
        if led == 0:
            logger.debug("Turning led 1 off")
            self.led.deactivate_torch()
        elif led == 1:
            logger.debug("Turning led 2 off")
            self.led.deactivate_torch()

    def led_on(self, led):
        if led == 0:
            logger.debug("Turning led 1 on")
            self.led.output_to_led1()
            self.led.activate_torch()
        elif led == 1:
            logger.debug("Turning led 2 on")
            self.led.output_to_led2()
            self.led.activate_torch()

    @logger.catch
    def treat_message(self):
        action = ""
        if self.light_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.light_client.msg["payload"]
            logger.debug(last_message)
            self.light_client.read_message()
            if "action" not in last_message:
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.light_client.client.publish("status/light", '{"status":"Error"}')
                return
            action = last_message["action"]
        if action == "on":
            # {"action":"on", "led":"1"}
            logger.info("Turning the light on.")
            if "led" not in last_message or last_message["led"] == "1":
                self.led_on(0)
                self.light_client.client.publish(
                    "status/light", '{"status":"Led 1: On"}'
                )
            elif last_message["led"] == "2":
                self.led_on(1)
                self.light_client.client.publish(
                    "status/light", '{"status":"Led 2: On"}'
                )
            else:
                self.light_client.client.publish(
                    "status/light", '{"status":"Error with led number"}'
                )
        elif action == "off":
            # {"action":"off", "led":"1"}
            logger.info("Turn the light off.")
            if "led" not in last_message or last_message["led"] == "1":
                self.led_off(0)
                self.light_client.client.publish(
                    "status/light", '{"status":"Led 1: Off"}'
                )
            elif last_message["led"] == "2":
                self.led_off(1)
                self.light_client.client.publish(
                    "status/light", '{"status":"Led 2: Off"}'
                )
            else:
                self.light_client.client.publish(
                    "status/light", '{"status":"Error with led number"}'
                )

        elif action != "":
            logger.warning(
                f"We did not understand the received request {action} - {last_message}"
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
    led.activate_torch()
    time.sleep(5)
    led.deactivate_torch()
    led.set_torch_current(10)
    led.activate_torch()
    time.sleep(5)
    led.deactivate_torch()
    RPi.GPIO.cleanup()
