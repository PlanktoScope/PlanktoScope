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

logger.info("planktoscope.light is loaded")

FREQUENCY = 50000
"""PWM Frequency in Hz"""
led0Pin = 18
led1Pin = 12


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
            self.pwm0.ChangeDutyCycle(0)
        elif self.led == 1:
            self.pwm1.ChangeDutyCycle(0)

    def on(self):
        if self.led == 0:
            self.pwm0.ChangeDutyCycle(100)
        elif self.led == 1:
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

    @logger.catch
    def __init__(self, event):
        """Initialize the Light class

        Args:
            event (multiprocessing.Event): shutdown event
        """
        super(LightProcess, self).__init__(name="light")

        logger.info("planktoscope.light is initialising")

        self.stop_event = event
        self.light_client = None
        self.led0 = pwm_led(0)
        self.led1 = pwm_led(1)

        logger.success("planktoscope.light is initialised and ready to go!")

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
            logger.info("Turn the light on.")
            if "led" not in last_message:
                self.led0.on()
                self.led1.on()
                self.light_client.client.publish(
                    "status/light", '{"status":"Led 1&2: On"}'
                )
            else:
                if last_message["led"] == "1":
                    self.led0.on()
                    self.light_client.client.publish(
                        "status/light", '{"status":"Led 1: On"}'
                    )
                elif last_message["led"] == "2":
                    self.led1.on()
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
            if "led" not in last_message:
                self.led0.off()
                self.led1.off()
                self.light_client.client.publish(
                    "status/light", '{"status":"Led 1&2: Off"}'
                )
            else:
                if last_message["led"] == "1":
                    self.led0.off()
                    self.light_client.client.publish(
                        "status/light", '{"status":"Led 1: Off"}'
                    )
                elif last_message["led"] == "2":
                    self.led1.off()
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
            topic="light/#", name="light_client"
        )

        # Publish the status "Ready" to via MQTT to Node-RED
        self.light_client.client.publish("status/light", '{"status":"Ready"}')

        logger.success("Light module is READY!")

        # This is the loop
        while not self.stop_event.is_set():
            self.treat_message()
            time.sleep(0.1)

        logger.info("Shutting down the light process")
        self.led0.stop()
        self.led1.stop()
        RPi.GPIO.cleanup()
        self.light_client.client.publish("status/light", '{"status":"Dead"}')
        self.light_client.shutdown()
        logger.success("Light process shut down! See you!")


# This is called if this script is launched directly
if __name__ == "__main__":
    led0.change_duty(50)
    led1.change_duty(0)