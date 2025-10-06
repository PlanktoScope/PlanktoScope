import multiprocessing
from multiprocessing.synchronize import Event
import os
import time
import typing

from loguru import logger

from .motor.motor import Motor

import mqtt

logger.info("planktoscope.pump is loaded")

"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2


class PumpProcess(multiprocessing.Process):
    # 507 steps per ml for PlanktoScope standard
    # 5200 for custom NEMA14 pump with 0.8mm ID Tube
    pump_steps_per_ml = 507
    # pump max speed is in ml/min
    pump_max_speed = 50

    def __init__(self, event: Event, configuration: dict[str, typing.Any]):
        super(PumpProcess, self).__init__()
        logger.info("Initialising the pump process")

        self.stop_event = event
        self.pump_started = False

        # parse the config data. If the key is absent, we are using the default value
        self.pump_steps_per_ml = configuration.get("pump_steps_per_ml", self.pump_steps_per_ml)
        self.pump_max_speed = configuration.get("pump_max_speed", self.pump_max_speed)

        # /dev/spidev0.0
        self.pump_stepper = Motor(pin=23, spi_bus=0, spi_device=0)

        # Set stepper controller max speed
        self.pump_stepper.acceleration = 2000
        self.pump_stepper.deceleration = self.pump_stepper.acceleration
        self.pump_stepper.speed = int(self.pump_max_speed * self.pump_steps_per_ml * 256 / 60)

        logger.info("Pump initialisation is over")

    def __message_pump(self, last_message):
        logger.debug("We have received a pumping command")
        if last_message["action"] == "stop":
            logger.debug("We have received a stop pump command")
            self.pump_stepper.shutdown()

            # Print status
            logger.info("The pump has been interrupted")

            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.pump_client.client.publish("status/pump", '{"status":"Interrupted"}')

        elif last_message["action"] == "move":
            logger.debug("We have received a move pump command")

            if (
                "direction" not in last_message
                or "volume" not in last_message
                or "flowrate" not in last_message
            ):
                logger.error(f"The received message has the wrong argument {last_message}")
                self.pump_client.client.publish(
                    "status/pump",
                    '{"status":"Error, the message is missing an argument"}',
                )
                return
            # Get direction from the different received arguments
            direction = last_message["direction"]
            # Get delay (in between steps) from the different received arguments
            volume = float(last_message["volume"])
            # Get number of steps from the different received arguments
            flowrate = float(last_message["flowrate"])
            if flowrate == 0:
                logger.error("The flowrate should not be == 0")
                self.pump_client.client.publish(
                    "status/pump", '{"status":"Error, The flowrate should not be == 0"}'
                )
                return

            # Print status
            logger.info("The pump is started.")
            self.pump(direction, volume, flowrate)
        else:
            logger.warning(f"The received message was not understood {last_message}")

    def treat_command(self):
        command = ""
        logger.info("We received a new message")
        last_message = self.pump_client.msg["payload"]  # type: ignore[index]
        logger.debug(last_message)
        command = self.pump_client.msg["topic"].split("/", 1)[1]  # type: ignore[index]
        logger.debug(command)
        self.pump_client.read_message()

        if command == "pump":
            self.__message_pump(last_message)
        elif command != "":
            logger.warning(f"We did not understand the received request {command} - {last_message}")

    # The pump max speed will be at about 400 full steps per second
    # This amounts to 0.9mL per seconds maximum, or 54mL/min
    # NEMA14 pump with 3 rollers is 0.509 mL per round, actual calculation at
    # Stepper is 200 steps/round, or 393steps/ml
    # https://www.wolframalpha.com/input/?i=pi+*+%280.8mm%29%C2%B2+*+54mm+*+3
    def pump(self, direction, volume, speed=pump_max_speed):
        """Moves the pump stepper

        Args:
            direction (string): direction of the pumping
            volume (int): volume to pump, in mL
            speed (int, optional): speed of pumping, in mL/min. Defaults to pump_max_speed.
        """

        logger.info(f"The pump will move {direction} for {volume}mL at {speed}mL/min")

        # Validation of inputs
        if direction not in ["FORWARD", "BACKWARD"]:
            logger.error("The direction command is not recognised")
            logger.error("It should be either FORWARD or BACKWARD")
            return

        # TMC5160 is configured for 256 microsteps
        nb_steps = round(self.pump_steps_per_ml * volume * 256, 0)
        logger.debug(f"The number of microsteps that will be applied is {nb_steps}")
        if speed > self.pump_max_speed:
            speed = self.pump_max_speed
            logger.warning(f"Pump speed has been clamped to a maximum safe speed of {speed}mL/min")
        steps_per_second = speed * self.pump_steps_per_ml * 256 / 60
        logger.debug(f"There will be a speed of {steps_per_second} steps per second")
        self.pump_stepper.speed = int(steps_per_second)

        # Publish the status "Started" to via MQTT to Node-RED
        self.pump_client.client.publish(
            "status/pump",
            f'{{"status":"Started", "duration":{nb_steps / steps_per_second}}}',
        )

        # Depending on direction, select the right direction for the pump
        if direction == "FORWARD":
            self.pump_started = True
            self.pump_stepper.go(FORWARD, nb_steps)
            return

        if direction == "BACKWARD":
            self.pump_started = True
            self.pump_stepper.go(BACKWARD, nb_steps)
            return

    @logger.catch
    def run(self):
        """This is the function that needs to be started to create a thread"""
        logger.info(f"The pump control process has been started in process {os.getpid()}")

        # # MQTT Service connection
        self.pump_client = mqtt.MQTT_Client(topic="actuator/pump", name="pump_client")

        # Publish the status "Ready" to via MQTT to Node-RED
        self.pump_client.client.publish("status/pump", '{"status":"Ready"}')

        logger.success("Pump is READY!")
        while not self.stop_event.is_set():
            if self.pump_client.new_message_received():
                self.treat_command()
            if self.pump_started and self.pump_stepper.at_goal():
                logger.success("The pump movement is over!")
                self.pump_client.client.publish(
                    "status/pump",
                    '{"status":"Done"}',
                )
                self.pump_started = False
                self.pump_stepper.release()
            time.sleep(0.01)
        logger.info("Shutting down the pump process")
        self.pump_client.client.publish("status/pump", '{"status":"Dead"}')
        self.pump_stepper.shutdown()
        self.pump_client.shutdown()
        logger.success("Pump process shut down! See you!")
