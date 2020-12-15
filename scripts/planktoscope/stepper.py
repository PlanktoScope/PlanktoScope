# Libraries to control the steppers for focusing and pumping
import adafruit_motor.stepper
import adafruit_motorkit
import time
import json
import os
import planktoscope.mqtt
import planktoscope.light
import multiprocessing
import RPi.GPIO

# Logger library compatible with multiprocessing
from loguru import logger

logger.info("planktoscope.stepper is loaded")


class StepperWaveshare:
    """A bipolar stepper motor using the Waveshare HAT."""

    def __init__(self, dir_pin, step_pin, enable_pin):
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.enable_pin = enable_pin

        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setup(
            [self.dir_pin, self.step_pin, self.enable_pin],
            RPi.GPIO.OUT,
            initial=RPi.GPIO.HIGH,
        )
        self.release()

    def release(self):
        """Releases all the coils so the motor can free spin, also won't use any power"""
        self.__digital_write(self.enable_pin, 1)

    def __digital_write(self, pin, value):
        RPi.GPIO.output(pin, value)

    def stop(self):
        self.__digital_write(self.enable_pin, 1)

    def onestep(self, *, direction=adafruit_motor.stepper.FORWARD, style=""):
        """Performs one step.
        :param int direction: Either `FORWARD` or `BACKWARD`"""

        if direction == adafruit_motor.stepper.FORWARD:
            self.__digital_write(self.enable_pin, 0)
            self.__digital_write(self.dir_pin, 1)
        elif direction == adafruit_motor.stepper.BACKWARD:
            self.__digital_write(self.enable_pin, 0)
            self.__digital_write(self.dir_pin, 0)
        else:
            logger.error(
                "The direction must be : adafruit_motor.stepper.FORWARD or adafruit_motor.stepper.BACKWARD"
            )
            self.release()
            return

        # This delay is just to make sure the chip had time to take the dir/enable pin
        # into account, min delay is 650ns
        time.sleep(0.000001)
        self.__digital_write(self.step_pin, True)
        # This delay is the minimal time high for the step impulse, 2µs
        time.sleep(0.000005)
        self.__digital_write(self.step_pin, False)


class stepper:
    def __init__(self, stepper, style=adafruit_motor.stepper.SINGLE, size=0):
        """Initialize the stepper class

        Args:
            stepper (adafruit_motorkit.Motorkit().stepper or StepperWaveshare): reference to the object that controls the stepper
            style (adafruit_motor.stepper): style of the movement SINGLE, DOUBLE, MICROSTEP
            size (int): maximum number of steps of this stepper (aka stage size). Can be 0 if not applicable
        """
        self.__stepper = stepper
        self.__style = style
        self.__size = size
        self.__position = 0
        self.__goal = 0
        self.__direction = ""
        self.__next_step_date = time.monotonic()
        self.__delay = 0
        # Make sure the stepper is released and do not use any power
        self.__stepper.release()

    def step_waiting(self):
        """Is there a step waiting to be actuated

        Returns:
            Bool: if time has come to push the step
        """
        return time.monotonic() > self.__next_step_date

    def at_goal(self):
        """Is the motor at its goal

        Returns:
            Bool: True if position and goal are identical
        """
        return self.__position == self.__goal

    def next_step_date(self):
        """set the next step date"""
        self.__next_step_date = self.__next_step_date + self.__delay

    def initial_step_date(self):
        """set the initial step date"""
        self.__next_step_date = time.monotonic() + self.__delay

    def move(self):
        """move the stepper

        Returns:
          Bool: True if the step done was the last one of the movement
        """
        if self.step_waiting() and not self.at_goal():
            self.__stepper.onestep(
                direction=self.__direction,
                style=self.__style,
            )
            if self.__direction == adafruit_motor.stepper.FORWARD:
                self.__position += 1
            elif self.__direction == adafruit_motor.stepper.BACKWARD:
                self.__position -= 1
            if not self.at_goal():
                self.next_step_date()
            else:
                logger.success("The stepper has reached its goal")
                self.__stepper.release()
                return True
        return False

    def go(self, direction, distance, delay):
        """move in the given direction for the given distance

        Args:
          direction (adafruit_motor.stepper): gives the movement direction
          distance
          delay
        """
        self.__delay = delay
        self.__direction = direction
        if self.__direction == adafruit_motor.stepper.FORWARD:
            self.__goal = self.__position + distance
        elif self.__direction == adafruit_motor.stepper.BACKWARD:
            self.__goal = self.__position - distance
        else:
            logger.error(f"The given direction is wrong {direction}")
        self.initial_step_date()

    def shutdown(self):
        """Shutdown everything ASAP"""
        self.__goal = self.__position
        self.__stepper.release()

    def release(self):
        self.__stepper.release()


class StepperProcess(multiprocessing.Process):

    focus_steps_per_mm = 40
    # 507 steps per ml for Planktonscope standard
    # 5200 for custom NEMA14 pump with 0.8mm ID Tube
    pump_steps_per_ml = 507
    # focus max speed is in mm/sec and is limited by the maximum number of pulses per second the Planktonscope can send
    focus_max_speed = 0.5
    # pump max speed is in ml/min
    pump_max_speed = 30

    stepper_type = "adafruit"

    def __init__(self, event):
        super(StepperProcess, self).__init__()
        logger.info("Initialising the stepper process")
        RPi.GPIO.setup([12, 4], RPi.GPIO.OUT, initial=RPi.GPIO.HIGH)

        self.stop_event = event

        if os.path.exists("/home/pi/PlanktonScope/hardware.json"):
            # load hardware.json
            with open("/home/pi/PlanktonScope/hardware.json", "r") as config_file:
                configuration = json.load(config_file)
                logger.debug(f"Hardware configuration loaded is {configuration}")
        else:
            logger.info(
                "The hardware configuration file doesn't exists, using defaults"
            )
            configuration = {}

        reverse = False
        microsteps = 16

        # parse the config data. If the key is absent, we are using the default value
        reverse = configuration.get("stepper_reverse", reverse)
        microsteps = configuration.get("microsteps", microsteps)
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
        self.stepper_type = configuration.get("stepper_type", self.stepper_type)

        # define the names for the 2 exsting steppers
        if self.stepper_type == "adafruit":
            logger.info("Loading the adafruit configuration")
            kit = adafruit_motorkit.MotorKit(steppers_microsteps=microsteps)
            if reverse:
                self.pump_stepper = stepper(kit.stepper2, adafruit_motor.stepper.DOUBLE)
                self.focus_stepper = stepper(
                    kit.stepper1, adafruit_motor.stepper.MICROSTEP, size=45
                )
            else:
                self.pump_stepper = stepper(kit.stepper1, adafruit_motor.stepper.DOUBLE)
                self.focus_stepper = stepper(
                    kit.stepper2, adafruit_motor.stepper.MICROSTEP, size=45
                )
        elif self.stepper_type == "waveshare":
            logger.info("Loading the waveshare configuration")
            logger.debug(
                f"Configured microsteps is {microsteps}, check the hardware switches if the stage does not move the intended distance"
            )
            if reverse:
                self.pump_stepper = stepper(
                    StepperWaveshare(dir_pin=24, step_pin=18, enable_pin=4)
                )
                self.focus_stepper = stepper(
                    StepperWaveshare(dir_pin=13, step_pin=19, enable_pin=12),
                    size=45,
                )
            else:
                self.pump_stepper = stepper(
                    StepperWaveshare(dir_pin=13, step_pin=19, enable_pin=12)
                )
                self.focus_stepper = stepper(
                    StepperWaveshare(dir_pin=24, step_pin=18, enable_pin=4),
                    size=45,
                )
        else:
            logger.error(
                "The stepper control type is not recognized. Should be 'adafruit' or 'waveshare'"
            )
            logger.error(f"{self.stepper_type} is what was supplied")
            return

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

            planktoscope.light.ready()

        elif last_message["action"] == "move":
            logger.debug("We have received a move pump command")
            planktoscope.light.pumping()

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

            planktoscope.light.ready()

        elif last_message["action"] == "move":
            logger.debug("We have received a move focus command")
            planktoscope.light.focusing()

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

            # Print status
            logger.info("The focus movement is started.")
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

            # If the command is "pump"
            if command == "pump":
                self.__message_pump(last_message)
            # If the command is "focus"
            elif command == "focus":
                self.__message_focus(last_message)
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
        if direction not in ["UP", "DOWN"]:
            logger.error("The direction command is not recognised")
            logger.error("It should be either UP or DOWN")
            return

        if distance > 45:
            logger.error("You are trying to move more than the stage physical size")
            return

        # We are going to use 32 microsteps, so we need to multiply by 32 the steps number
        nb_steps = round(self.focus_steps_per_mm * distance * 32, 0)
        logger.debug(f"The number of steps that will be applied is {nb_steps}")
        steps_per_second = speed * self.focus_steps_per_mm * 32
        logger.debug(f"There will be a speed of {steps_per_second} steps per second")

        if steps_per_second > 400:
            steps_per_second = 400
            logger.warning("The requested speed is faster than the maximum safe speed")
            logger.warning(
                f"The speed of the motor is going to be limited to {steps_per_second/32/self.focus_steps_per_mm}mm/sec"
            )

        # On linux, the minimal acceptable delay managed by the system is 0.1ms
        # see https://stackoverflow.com/questions/1133857/how-accurate-is-pythons-time-sleep
        # However we have a fixed delay of at least 2.5ms per step due to the library
        # Our maximum speed is thus about 400 pulses per second or 0.5mm/sec of stage speed
        if self.stepper_type == "adafruit":
            delay = max((1 / steps_per_second) - 0.0025, 0)
        else:
            delay = 1 / steps_per_second
        logger.debug(f"The delay between two steps is {delay}s")

        # Publish the status "Started" to via MQTT to Node-RED
        self.actuator_client.client.publish(
            "status/focus",
            f'{{"status":"Started", "duration":{nb_steps / steps_per_second}}}',
        )

        # Depending on direction, select the right direction for the focus
        if direction == "UP":
            self.focus_stepper.go(adafruit_motor.stepper.FORWARD, nb_steps, delay)

        if direction == "DOWN":
            self.focus_stepper.go(adafruit_motor.stepper.BACKWARD, nb_steps, delay)

    # The pump max speed will be at about 400 full steps per second
    # This amounts to 0.9mL per seconds maximum, or 54mL/min
    # NEMA14 pump with 3 rollers is 0.509 mL per round, actual calculation at
    # Stepper is 200 steps/round, or 393steps/ml
    # https://www.wolframalpha.com/input/?i=pi+*+%280.8mm%29%C2%B2+*+54mm+*+3
    def pump(self, direction, volume, speed=pump_max_speed):
        """moves the pump stepper

        direction is either FORWARD or BACKWARD
        volume is in mL
        speed is in mL/min"""

        logger.info(f"The pump will move {direction} for {volume}mL at {speed}mL/min")

        # Validation of inputs
        if direction not in ["FORWARD", "BACKWARD"]:
            logger.error("The direction command is not recognised")
            logger.error("It should be either FORWARD or BACKWARD")
            return

        nb_steps = round(self.pump_steps_per_ml * volume, 0)
        logger.debug(f"The number of steps that will be applied is {nb_steps}")
        steps_per_second = speed * self.pump_steps_per_ml / 60
        logger.debug(f"There will be a speed of {steps_per_second} steps per second")

        if steps_per_second > 400:
            steps_per_second = 400
            logger.warning("The requested speed is faster than the maximum safe speed")
            logger.warning(
                f"The speed of the motor is going to be limited to {steps_per_second*60/self.pump_steps_per_ml}mL/min"
            )
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
        if self.stepper_type == "adafruit":
            delay = max((1 / steps_per_second) - 0.0025, 0)
        else:
            delay = 1 / steps_per_second
        logger.debug(f"The delay between two steps is {delay}s")

        # Publish the status "Started" to via MQTT to Node-RED
        self.actuator_client.client.publish(
            "status/pump",
            f'{{"status":"Started", "duration":{nb_steps / steps_per_second}}}',
        )

        # Depending on direction, select the right direction for the focus
        if direction == "FORWARD":
            self.pump_stepper.go(adafruit_motor.stepper.FORWARD, nb_steps, delay)

        if direction == "BACKWARD":
            self.pump_stepper.go(adafruit_motor.stepper.BACKWARD, nb_steps, delay)

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
        delay = 0.001
        while not self.stop_event.is_set():
            if self.actuator_client.new_message_received():
            self.treat_command()
            if self.pump_stepper.move():
                delay = 0.0001
                planktoscope.light.ready()
                self.actuator_client.client.publish(
                    "status/pump",
                    '{"status":"Done"}',
                )
            if self.focus_stepper.move():
                delay = 0.0001
                planktoscope.light.ready()
                self.actuator_client.client.publish(
                    "status/focus",
                    '{"status":"Done"}',
                )
            time.sleep(delay)
            delay = 0.001
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