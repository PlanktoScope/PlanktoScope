import multiprocessing
import os
import time

from loguru import logger

from planktoscope.stepper import stepper

from . import mqtt

logger.info("planktoscope.focus is loaded")

"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2


class FocusProcess(multiprocessing.Process):
    focus_steps_per_mm = 40
    # focus max speed is in mm/sec and is limited by the maximum number of pulses per second the PlanktoScope can send
    focus_max_speed = 5

    def __init__(self, event, configuration):
        super(FocusProcess, self).__init__()
        logger.info("Initialising the focus process")

        self.stop_event = event
        self.focus_started = False

        # parse the config data. If the key is absent, we are using the default value
        self.focus_steps_per_mm = configuration.get("focus_steps_per_mm", self.focus_steps_per_mm)
        self.focus_max_speed = configuration.get("focus_max_speed", self.focus_max_speed)

        # /dev/spidev0.1
        self.focus_stepper = stepper(pin=5, spi_bus=0, spi_device=1, size=45)

        # Set stepper controller max speed
        self.focus_stepper.acceleration = 1000
        self.focus_stepper.deceleration = self.focus_stepper.acceleration
        self.focus_stepper.speed = self.focus_max_speed * self.focus_steps_per_mm * 256

        logger.info("Focus initialisation is over")

    def __message_focus(self, last_message):
        logger.debug("We have received a focusing request")
        # If a new received command is "focus" but args contains "stop" we stop!
        if last_message["action"] == "stop":
            logger.debug("We have received a stop focus command")
            self.focus_stepper.shutdown()

            # Print status
            logger.info("The focus has been interrupted")

            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.focus_client.client.publish("status/focus", '{"status":"Interrupted"}')

        elif last_message["action"] == "move":
            logger.debug("We have received a move focus command")

            if "direction" not in last_message or "distance" not in last_message:
                logger.error(f"The received message has the wrong argument {last_message}")
                self.focus_client.client.publish("status/focus", '{"status":"Error"}')
            # Get direction from the different received arguments
            direction = last_message["direction"]
            # Get number of steps from the different received arguments
            distance = float(last_message["distance"])

            speed = float(last_message["speed"]) if "speed" in last_message else 0

            # Print status
            logger.info("The focus movement is started.")
            if speed:
                self.focus(direction, distance, speed)
            else:
                self.focus(direction, distance)
        else:
            logger.warning(f"The received message was not understood {last_message}")

    def treat_command(self):
        command = ""
        logger.info("We received a new message")
        last_message = self.focus_client.msg["payload"]  # type: ignore[index]
        logger.debug(last_message)
        command = self.focus_client.msg["topic"].split("/", 1)[1]  # type: ignore[index]
        logger.debug(command)
        self.focus_client.read_message()

        if command == "focus":
            self.__message_focus(last_message)
        elif command != "":
            logger.warning(f"We did not understand the received request {command} - {last_message}")

    def focus(self, direction, distance, speed=focus_max_speed):
        """Moves the focus stepper

        direction is either UP or DOWN
        distance is received in mm
        speed is in mm/sec

        Args:
            direction (string): either UP or DOWN
            distance (int): distance to move the stage, in mm
            speed (int, optional): max speed of the stage, in mm/sec. Defaults to focus_max_speed.
        """

        logger.info(f"The focus stage will move {direction} for {distance}mm at {speed}mm/sec")

        # Validation of inputs
        if direction not in ["UP", "DOWN"]:
            logger.error("The direction command is not recognised")
            logger.error("It should be either UP or DOWN")
            return

        if distance > 45:
            logger.error("You are trying to move more than the stage physical size")
            return

        # We are going to use 256 microsteps, so we need to multiply by 256 the steps number
        nb_steps = round(self.focus_steps_per_mm * distance * 256, 0)
        logger.debug(f"The number of microsteps that will be applied is {nb_steps}")
        if speed > self.focus_max_speed:
            speed = self.focus_max_speed
            logger.warning(
                f"Focus stage speed has been clamped to a maximum safe speed of {speed} mm/sec"
            )
        steps_per_second = speed * self.focus_steps_per_mm * 256
        logger.debug(f"There will be a speed of {steps_per_second} steps per second")
        self.focus_stepper.speed = int(steps_per_second)

        # Publish the status "Started" to via MQTT to Node-RED
        self.focus_client.client.publish(
            "status/focus",
            f'{{"status":"Started", "duration":{nb_steps / steps_per_second}}}',
        )

        # Depending on direction, select the right direction for the focus
        if direction == "UP":
            self.focus_started = True
            self.focus_stepper.go(FORWARD, nb_steps)
            return

        if direction == "DOWN":
            self.focus_started = True
            self.focus_stepper.go(BACKWARD, nb_steps)
            return

    @logger.catch
    def run(self):
        """This is the function that needs to be started to create a thread"""
        logger.info(f"The focus control process has been started in process {os.getpid()}")

        # MQTT Service connection
        self.focus_client = mqtt.MQTT_Client(topic="actuator/focus", name="focus_client")

        # Publish the status "Ready" to via MQTT to Node-RED
        self.focus_client.client.publish("status/focus", '{"status":"Ready"}')

        logger.success("Focus is READY!")
        while not self.stop_event.is_set():
            if self.focus_client.new_message_received():
                self.treat_command()
            if self.focus_started and self.focus_stepper.at_goal():
                logger.success("The focus movement is over!")
                self.focus_client.client.publish(
                    "status/focus",
                    '{"status":"Done"}',
                )
                self.focus_started = False
                self.focus_stepper.release()
            time.sleep(0.01)
        logger.info("Shutting down the focus process")
        self.focus_client.client.publish("status/focus", '{"status":"Dead"}')
        self.focus_stepper.shutdown()
        self.focus_client.shutdown()
        logger.success("Focus process shut down! See you!")
