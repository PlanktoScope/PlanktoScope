# Libraries to control the steppers for focusing and pumping
import time
import json
import os
import planktoscope.mqtt
import multiprocessing
import RPi.GPIO

import shush

# Logger library compatible with multiprocessing
from loguru import logger

logger.info("planktoscope.stepper is loaded")


"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2
"""Stepper controller 1"""
STEPPER1 = 0
""""Stepper controller 2"""
STEPPER2 = 1


class stepper:
    def __init__(self, stepper, size=0):
        """Initialize the stepper class

        Args:
            stepper (either STEPPER1 or STEPPER2): reference to the object that controls the stepper
            size (int): maximum number of steps of this stepper (aka stage size). Can be 0 if not applicable
        """
        self.__stepper = shush.Motor(stepper)
        self.__size = size
        self.__goal = 0
        self.__direction = ""
        self.__stepper.disable_motor()

    def at_goal(self):
        """Is the motor at its goal

        Returns:
            Bool: True if position and goal are identical
        """
        return self.__stepper.get_position() == self.__goal

    def is_moving(self):
        """is the stepper in movement?

        Returns:
          Bool: True if the stepper is moving
        """
        return self.__stepper.get_velocity() != 0

    def go(self, direction, distance):
        """move in the given direction for the given distance

        Args:
          direction: gives the movement direction
          distance:
        """
        self.__direction = direction
        if self.__direction == FORWARD:
            self.__goal = int(self.__stepper.get_position() + distance)
        elif self.__direction == BACKWARD:
            self.__goal = int(self.__stepper.get_position() - distance)
        else:
            logger.error(f"The given direction is wrong {direction}")
        self.__stepper.enable_motor()
        self.__stepper.go_to(self.__goal)

    def shutdown(self):
        """Shutdown everything ASAP"""
        self.__stepper.stop_motor()
        self.__stepper.disable_motor()
        self.__goal = self.__stepper.get_position()

    def release(self):
        self.__stepper.disable_motor()

    @property
    def speed(self):
        return self.__stepper.ramp_VMAX

    @speed.setter
    def speed(self, speed):
        """Change the stepper speed

        Args:
            speed (int): speed of the movement by the stepper, in microsteps unit/s
        """
        logger.debug(f"Setting stepper speed to {speed}")
        self.__stepper.ramp_VMAX = int(speed)

    @property
    def acceleration(self):
        return self.__stepper.ramp_AMAX

    @acceleration.setter
    def acceleration(self, acceleration):
        """Change the stepper acceleration

        Args:
            acceleration (int): acceleration reachable by the stepper, in microsteps unit/s²
        """
        logger.debug(f"Setting stepper acceleration to {acceleration}")
        self.__stepper.ramp_AMAX = int(acceleration)

    @property
    def deceleration(self):
        return self.__stepper.ramp_DMAX

    @deceleration.setter
    def deceleration(self, deceleration):
        """Change the stepper deceleration

        Args:
            deceleration (int): deceleration reachable by the stepper, in microsteps unit/s²
        """
        logger.debug(f"Setting stepper deceleration to {deceleration}")
        self.__stepper.ramp_DMAX = int(deceleration)


class StepperProcess(multiprocessing.Process):
    focus_steps_per_mm = 40
    # 507 steps per ml for PlanktoScope standard
    # 5200 for custom NEMA14 pump with 0.8mm ID Tube
    pump_steps_per_ml = 507
    # focus max speed is in mm/sec and is limited by the maximum number of pulses per second the PlanktoScope can send
    focus_max_speed = 5
    # pump max speed is in ml/min
    pump_max_speed = 50

    def __init__(self, event):
        super(StepperProcess, self).__init__()
        logger.info("Initialising the stepper process")

        self.stop_event = event
        self.focus_started = False
        self.pump_started = False

        if os.path.exists("/home/pi/PlanktoScope/hardware.json"):
            # load hardware.json
            with open("/home/pi/PlanktoScope/hardware.json", "r") as config_file:
                configuration = json.load(config_file)
                logger.debug(f"Hardware configuration loaded is {configuration}")
        else:
            logger.info(
                "The hardware configuration file doesn't exists, using defaults"
            )
            configuration = {}

        reverse = False

        # parse the config data. If the key is absent, we are using the default value
        reverse = configuration.get("stepper_reverse", reverse)
        self.focus_steps_per_mm = configuration.get(
            "focus_steps_per_mm", self.focus_steps_per_mm
        )
        self.pump_steps_per_ml = configuration.get(
            "pump_steps_per_ml", self.pump_steps_per_ml
        )
        self.focus_max_speed = configuration.get(
            "focus_max_speed", self.focus_max_speed
        )
        self.pump_max_speed = configuration.get("pump_max_speed", self.pump_max_speed)

        # define the names for the 2 exsting steppers
        if reverse:
            self.pump_stepper = stepper(STEPPER2)
            self.focus_stepper = stepper(STEPPER1, size=45)
        else:
            self.pump_stepper = stepper(STEPPER1)
            self.focus_stepper = stepper(STEPPER2, size=45)

        # Set stepper controller max speed

        self.focus_stepper.acceleration = 1000
        self.focus_stepper.deceleration = self.focus_stepper.acceleration
        self.focus_stepper.speed = self.focus_max_speed * self.focus_steps_per_mm * 256

        self.pump_stepper.acceleration = 2000
        self.pump_stepper.deceleration = self.pump_stepper.acceleration
        self.pump_stepper.speed = (
            self.pump_max_speed * self.pump_steps_per_ml * 256 / 60
        )

        logger.info(f"Stepper initialisation is over")

    def __message_pump(self, last_message):
        logger.debug("We have received a pumping command")
        if last_message["action"] == "stop":
            logger.debug("We have received a stop pump command")
            self.pump_stepper.shutdown()

            # Print status
            logger.info("The pump has been interrupted")

            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.actuator_client.client.publish(
                "status/pump", '{"status":"Interrupted"}'
            )

        elif last_message["action"] == "move":
            logger.debug("We have received a move pump command")

            if (
                "direction" not in last_message
                or "volume" not in last_message
                or "flowrate" not in last_message
            ):
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.actuator_client.client.publish(
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
                logger.error(f"The flowrate should not be == 0")
                self.actuator_client.client.publish(
                    "status/pump", '{"status":"Error, The flowrate should not be == 0"}'
                )
                return

            # Print status
            logger.info("The pump is started.")
            self.pump(direction, volume, flowrate)
        else:
            logger.warning(f"The received message was not understood {last_message}")

    def __message_focus(self, last_message):
        logger.debug("We have received a focusing request")
        # If a new received command is "focus" but args contains "stop" we stop!
        if last_message["action"] == "stop":
            logger.debug("We have received a stop focus command")
            self.focus_stepper.shutdown()

            # Print status
            logger.info("The focus has been interrupted")

            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.actuator_client.client.publish(
                "status/focus", '{"status":"Interrupted"}'
            )

        elif last_message["action"] == "move":
            logger.debug("We have received a move focus command")

            if "direction" not in last_message or "distance" not in last_message:
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.actuator_client.client.publish(
                    "status/focus", '{"status":"Error"}'
                )
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
        last_message = self.actuator_client.msg["payload"]
        logger.debug(last_message)
        command = self.actuator_client.msg["topic"].split("/", 1)[1]
        logger.debug(command)
        self.actuator_client.read_message()

        if command == "pump":
            self.__message_pump(last_message)
        elif command == "focus":
            self.__message_focus(last_message)
        elif command != "":
            logger.warning(
                f"We did not understand the received request {command} - {last_message}"
            )

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

        logger.info(
            f"The focus stage will move {direction} for {distance}mm at {speed}mm/sec"
        )

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
        self.actuator_client.client.publish(
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
            logger.warning(
                f"Pump speed has been clamped to a maximum safe speed of {speed}mL/min"
            )
        steps_per_second = speed * self.pump_steps_per_ml * 256 / 60
        logger.debug(f"There will be a speed of {steps_per_second} steps per second")
        self.pump_stepper.speed = int(steps_per_second)

        # Publish the status "Started" to via MQTT to Node-RED
        self.actuator_client.client.publish(
            "status/pump",
            f'{{"status":"Started", "duration":{nb_steps / steps_per_second}}}',
        )

        # Depending on direction, select the right direction for the focus
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
        logger.info(
            f"The stepper control process has been started in process {os.getpid()}"
        )

        # Creates the MQTT Client
        # We have to create it here, otherwise when the process running run is started
        # it doesn't see changes and calls made by self.actuator_client because this one
        # only exist in the master process
        # see https://stackoverflow.com/questions/17172878/using-pythons-multiprocessing-process-class
        self.actuator_client = planktoscope.mqtt.MQTT_Client(
            topic="actuator/#", name="actuator_client"
        )
        # Publish the status "Ready" to via MQTT to Node-RED
        self.actuator_client.client.publish("status/pump", '{"status":"Ready"}')
        # Publish the status "Ready" to via MQTT to Node-RED
        self.actuator_client.client.publish("status/focus", '{"status":"Ready"}')

        logger.success("Stepper is READY!")
        while not self.stop_event.is_set():
            if self.actuator_client.new_message_received():
                self.treat_command()
            if self.pump_started and self.pump_stepper.at_goal():
                logger.success(f"The pump movement is over!")
                self.actuator_client.client.publish(
                    "status/pump",
                    '{"status":"Done"}',
                )
                self.pump_started = False
                self.pump_stepper.release()
            if self.focus_started and self.focus_stepper.at_goal():
                logger.success(f"The focus movement is over!")
                self.actuator_client.client.publish(
                    "status/focus",
                    '{"status":"Done"}',
                )
                self.focus_started = False
                self.pump_stepper.release()
            time.sleep(0.01)
        logger.info("Shutting down the stepper process")
        self.actuator_client.client.publish("status/pump", '{"status":"Dead"}')
        self.actuator_client.client.publish("status/focus", '{"status":"Dead"}')
        self.pump_stepper.shutdown()
        self.focus_stepper.shutdown()
        self.actuator_client.shutdown()
        logger.success("Stepper process shut down! See you!")


# This is called if this script is launched directly
if __name__ == "__main__":
    # TODO This should be a test suite for this library
    # Starts the stepper thread for actuators
    # This needs to be in a threading or multiprocessing wrapper
    stepper_thread = StepperProcess()
    stepper_thread.start()
    stepper_thread.join()
