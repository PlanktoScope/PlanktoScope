# Libraries to control the steppers for focusing and pumping
import adafruit_motor
import adafruit_motorkit
import time
import json
import planktoscope.mqtt
import planktoscope.light
import multiprocessing

# Logger library compatible with multiprocessing
from loguru import logger

logger.info("planktoscope.stepper is loaded")


class stepper:
    def __init__(self, stepper, style, size=0):
        """Initialize the stepper class

        Args:
            stepper (adafruit_motorkit.Motorkit().stepper): reference to the object that controls the stepper
            style (adafruit.): style of the movement SINGLE, DOUBLE, MICROSTEP
            size (int): maximum number of steps of this stepper (aka stage size). Can be 0 if not applicable
        """
        self.__stepper = stepper
        self.__style = style
        self.__size = size
        self.__position = 0
        self.__goal = 0
        self.__direction = ""
        self.__next_step_date = time.monotonic_ns()
        self.__delay = 0
        # Make sure the stepper is released and do not use any power
        self.__stepper.release()

    def step_waiting():
        """Is there a step waiting to be actuated

        Returns:
            Bool: if time has come to push the step
        """
        return time.monotonic_ns() > self.__next_step_date

    def at_goal():
        """Is the motor at its goal

        Returns:
            Bool: difference between position and goal
        """
        return self.__position != self.__goal

    def next_step_date():
        """set the next step date"""
        self.__next_step_date = self.__next_step_date + self.__delay * 1000

    def initial_step_date():
        """set the initial step date"""
        self.__next_step_date = time.monotonic_ns() + self.__delay * 1000

    def move():
        """move the stepper"""
        if self.step_waiting():
            self.__stepper.onestep(
                direction=self.__direction,
                style=self.__style,
            )
            if self.__direction == "FORWARD":
                self.__position += 1
            elif self.__direction == "BACKWARD":
                self.__position -= 1
            if self.at_goal():
                logger.info("The stepper has reached its goal")
                self.__stepper.release()
            else:
                self.next_step_date()

    def go(direction, distance, delay):
        """move in the given direction for the given distance

        direction (adafruit_motor.stepper): gives the movement direction
        """
        self.__delay = delay
        self.__direction = direction
        if self.__direction == "FORWARD":
            self.__goal = position + distance
        elif self.__direction == "BACKWARD":
            self.__goal = position - distance
        else:
            logger.error(f"The given direction is wrong {direction}")
        self.initial_step_date()


class StepperProcess(multiprocessing.Process):

    focus_steps_per_mm = 40
    # 507 steps per ml for Planktonscope standard
    # 614 for custom NEMA14 pump with 0.8mm ID Tube
    pump_steps_per_ml = 507
    # focus max speed is in mm/sec and is limited by the maximum number of pulses per second the Planktonscope can send
    focus_max_speed = 0.5
    # pump max speed is in ml/min
    pump_max_speed = 30

    def __init__(self, event):
        super(StepperProcess, self).__init__()

        self.stop_event = event

        # load config.json
        with open("/home/pi/PlanktonScope/hardware.json", "r") as config_file:
            configuration = json.load(config_file)
            logger.debug(f"Hardware configuration loaded is {configuration}")

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
        kit = adafruit_motorkit.MotorKit()
        if reverse:
            self.pump_stepper = stepper(kit.stepper2)
            self.focus_stepper = stepper(kit.stepper1, 45)
        else:
            self.pump_stepper = stepper(kit.stepper1)
            self.focus_stepper = stepper(kit.stepper2, 45)

        logger.debug(f"Stepper initialisation is over")

    def treat_command(self):
        command = ""
        if self.actuator_client.is_new_message():
            logger.info("We received a new message")
            last_message = json.load(self.actuator_client.msg.payload)
            logger.debug(last_message)
            command = self.actuator_client.msg.topic.split("/", 1)[1]
            logger.debug(command)
            self.actuator_client.read_message()

        # If the command is "pump"
        if command == "pump":
            logger.debug("We have received a pumping command")
            if last_message.action == "stop":
                logger.debug("We have received a stop pump command")
                self.pump_stepper.stepper.release()
                self.pump_stepper.goal = self.pump_stepper.position

                # Print status
                logger.info("The pump has been interrupted")

                # Publish the status "Interrompted" to via MQTT to Node-RED
                self.actuator_client.client.publish(
                    "status/pump", "{'status':'Interrupted'}"
                )

                # Set the LEDs as Green
                planktoscope.light.setRGB(0, 255, 0)

            elif last_message.action == "move":
                logger.debug("We have received a move pump command")
                # Set the LEDs as Blue
                planktoscope.light.setRGB(0, 0, 255)

                # Get direction from the different received arguments
                direction = last_message.direction
                # Get delay (in between steps) from the different received arguments
                volume = float(last_message.volume)
                # Get number of steps from the different received arguments
                flow_rate = float(last_message.flow_rate)

                # Publish the status "Start" to via MQTT to Node-RED
                self.actuator_client.client.publish("status/pump", "{'status':'Start'}")

                # Print status
                logger.info("The pump is started.")
                pump(direction, volume, flow_rate)
            else:
                logger.warning(
                    f"The received message was not understood {last_message}"
                )

        # If the command is "focus"
        elif command == "focus":
            logger.debug("We have received a focusing request")
            # If a new received command is "focus" but args contains "stop" we stop!
            if last_message.action == "stop":
                logger.debug("We have received a stop focus command")
                self.focus_stepper.stepper.release()
                self.focus_stepper.goal = self.focus_stepper.position

                # Print status
                logger.info("The focus has been interrupted")

                # Publish the status "Interrompted" to via MQTT to Node-RED
                self.actuator_client.client.publish(
                    "status/focus", "{'status':'Interrupted'}"
                )

                # Set the LEDs as Green
                planktoscope.light.setRGB(0, 255, 0)

            elif last_message.action == "move":
                logger.debug("We have received a move focus command")
                # Set the LEDs as Yellow
                planktoscope.light.setRGB(255, 255, 0)

                # Get direction from the different received arguments
                direction = last_message.direction
                # Get number of steps from the different received arguments
                distance = float(last_message.distance)

                # Publish the status "Start" to via MQTT to Node-RED
                self.actuator_client.client.publish(
                    "status/focus", "{'status':'Start'}"
                )

                # Print status
                logger.info("The focus movement is started.")
                focus(direction, distance)
            else:
                logger.warning(
                    f"The received message was not understood {last_message}"
                )
        elif command != "":
            logger.warning(
                f"We did not understand the received request {command} - {last_message}"
            )

    def focus(self, direction, distance, speed=focus_max_speed):
        """moves the focus stepper

        direction is either UP or DOWN
        distance is received in mm
        speed is in mm/sec"""

        logger.info(
            f"The focus stage will move {direction} for {distance}mm at {speed}mm/sec"
        )

        # Validation of inputs
        if direction != "UP" and direction != "DOWN":
            logger.error("The direction command is not recognised")
            logger.error("It should be either UP or DOWN")
            return

        if distance > 45:
            logger.error("You are trying to move more than the stage physical size")
            return

        if speed > self.focus_max_speed:
            speed = self.focus_max_speed
            logger.warning("The requested speed is faster than the maximum safe speed")
            logger.warning(f"The speed of the motor is going to be limited to {speed}")

        # We are going to use microsteps, so we need to multiply by 16 the steps number
        nb_steps = self.focus_steps_per_mm * distance * 16
        logger.debug(f"The number of steps that will be applied is {nb_steps}")
        steps_per_second = speed * self.focus_steps_per_mm * 16
        logger.debug(f"There will be a speed of {steps_per_second} steps per second")

        # On linux, the minimal acceptable delay managed by the system is 0.1ms
        # see https://stackoverflow.com/questions/1133857/how-accurate-is-pythons-time-sleep
        # However we have a fixed delay of at least 2.5ms per step due to the library
        # Our maximum speed is thus about 400 pulses per second or 0.5mm/sec of stage speed
        delay = max((1 / steps_per_second) - 0.0025, 0)
        logger.debug(f"The delay between two steps is {delay}")

        # Depending on direction, select the right direction for the focus
        if direction == "UP":
            self.focus_stepper.go(adafruit_motor.stepper.FORWARD, nb_steps, delay)

        if direction == "DOWN":
            self.focus_stepper.go(adafruit_motor.stepper.BACKWARD, nb_steps, delay)

    # The pump max speed will be at about 400 full steps per second
    # This amounts to 0.65mL per seconds maximum
    # NEMA14 pump with 3 rollers is 0.3257 mL per round, actual calculation at
    # https://www.wolframalpha.com/input/?i=pi+*+%280.8mm%29%C2%B2+*+54mm+*+3
    def pump(self, direction, volume, speed=pump_max_speed):
        """moves the pump stepper

        direction is either FORWARD or BACKWARD
        volume is in mL
        speed is in mL/min"""

        logger.info(f"The pump will move {direction} for {volume}mL at {speed}mL/min")

        # Validation of inputs
        if direction != "FORWARD" and direction != "BACKWARD":
            logger.error("The direction command is not recognised")
            logger.error("It should be either FORWARD or BACKWARD")
            return

        if speed > self.pump_max_speed:
            speed = self.pump_max_speed
            logger.warning("The requested speed is faster than the maximum safe speed")
            logger.warning(f"The speed of the motor is going to be limited to {speed}")

        nb_steps = self.pump_steps_per_ml * volume
        logger.debug(f"The number of steps that will be applied is {nb_steps}")
        steps_per_second = speed * self.pump_steps_per_ml / 60
        logger.debug(f"There will be a speed of {steps_per_second} steps per second")

        # On linux, the minimal acceptable delay managed by the system is 0.1ms
        # see https://stackoverflow.com/questions/1133857/how-accurate-is-pythons-time-sleep
        # However we have a fixed delay of at least 2.5ms per step due to the library
        # Our maximum speed is thus about 400 pulses per second or 2 turn per second of the pump
        # 10mL => 6140 pas
        # 1.18gr => 1.18mL
        # Actual pas/mL => 5200
        # Max speed is 400 steps/sec, or 4.6mL/min
        # 15mL at 3mL/min
        # nb_steps = 5200 * 15 = 78000
        # sps = 3mL/min * 5200s/mL = 15600s/min / 60 => 260sps
        delay = max((1 / steps_per_second) - 0.0025, 0)
        logger.debug(f"The delay between two steps is {delay}")

        # Depending on direction, select the right direction for the focus
        if direction == "FORWARD":
            self.pump_stepper.go(adafruit_motor.stepper.FORWARD, nb_steps, delay)

        if direction == "BACKWARD":
            self.pump_stepper.go(adafruit_motor.stepper.BACKWARD, nb_steps, delay)

    def run(self):
        """This is the function that needs to be started to create a thread

        This function runs for perpetuity. For now, it has no exit methods
        (hence no cleanup is performed on exit/kill). However, atexit can
        probably be used for this. See https://docs.python.org/3.8/library/atexit.html
        Eventually, the __del__ method could be used, if this module is
        made into a class.
        """

        # Creates the MQTT Client
        self.actuator_client = planktoscope.mqtt.MQTT_Client(
            topic="actuator/#", name="actuator_client"
        )
        self.actuator_client.connect()

        logger.info("The stepper control thread has been started")
        while True:
            # check if a new message has been received
            self.treat_command()
            self.pump_stepper.move()
            self.focus_stepper.move()
            if self.stop_event.is_set():
                logger.info("shutting down the process")
                # TODO add the functions for releasing the motors here
                        break


# This is called if this script is launched directly
if __name__ == "__main__":
    # Starts the stepper thread for actuators
    # This needs to be in a threading or multiprocessing wrapper
    stepper_thread = StepperProcess()
    stepper_thread.start()
    stepper_thread.join()