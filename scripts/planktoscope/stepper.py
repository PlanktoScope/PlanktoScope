# Libraries to control the steppers for focusing and pumping
import adafruit_motor
import adafruit_motorkit
import time
import json
import planktoscope.mqtt
import planktoscope.light
import multiprocessing


class StepperProcess(multiprocessing.Process):

    focus_steps_per_mm = 40
    # 507 steps per ml for Planktonscope standard
    # 614 for custom NEMA14 pump with 0.8mm ID Tube
    pump_steps_per_ml = 507
    # focus max speed is in mm/sec and is limited by the maximum number of pulses per second the Planktonscope can send
    focus_max_speed = 0.5
    # pump max speed is in ml/min
    pump_max_speed = 30

    def __init__(self):
        super(StepperProcess, self).__init__()

        # load config.json
        with open("/home/pi/PlanktonScope/hardware.json", "r") as config_file:
            configuration = json.load(config_file)

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
            self.pump_stepper = kit.stepper2
            self.focus_stepper = kit.stepper1
        else:
            self.pump_stepper = kit.stepper1
            self.focus_stepper = kit.stepper2

        # Make sure the steppers are released and do not use any power
        self.pump_stepper.release()
        self.focus_stepper.release()

    def focus(self, direction, distance, speed=focus_max_speed):
        """moves the focus stepper

        direction is either UP or DOWN
        distance is received in mm
        speed is in mm/sec"""

        print(f"the focus stage will move {direction} for {distance}mm")

        # Validation of inputs
        if direction != "UP" and direction != "DOWN":
            print("ERROR! The direction command is not recognised")
            return

        if distance > 45:
            print("ERROR! You are trying to move more than the stage physical size")
            return

        if speed > self.focus_max_speed:
            speed = self.focus_max_speed
            print("WARNING! You requested speed is faster than the maximum safe speed")
            print("The speed of the motor is going to be limited")

        counter = 0

        # We are going to use microsteps, so we need to multiply by 16 the steps number
        nb_steps = self.focus_steps_per_mm * distance * 16
        steps_per_second = speed * self.focus_steps_per_mm * 16

        # On linux, the minimal acceptable delay managed by the system is 0.1ms
        # see https://stackoverflow.com/questions/1133857/how-accurate-is-pythons-time-sleep
        # However we have a fixed delay of at least 2.5ms per step due to the library
        # Our maximum speed is thus about 400 pulses per second or 0.5mm/sec of stage speed
        delay = max((1 / steps_per_second) - 0.0025, 0)

        # Depending on direction, select the right direction for the focus
        if direction == "UP":
            direction = adafruit_motor.stepper.FORWARD

        if direction == "DOWN":
            direction = adafruit_motor.stepper.BACKWARD

        while True:
            # Actuate the focus for one microstep in the right direction
            self.focus_stepper.onestep(
                direction=direction, style=adafruit_motor.stepper.MICROSTEP
            )
            # Increment the counter
            counter += 1
            time.sleep(delay)
            ####################################################################
            # If counter reach the number of step, break
            if counter > nb_steps:
                # Release the focus steppers to stop power draw
                self.focus_stepper.release()
                break

    # The pump max speed will be at about 400 full steps per second
    # This amounts to 0.65mL per seconds maximum
    # NEMA14 pump with 3 rollers is 0.3257 mL per round, actual calculation at
    # https://www.wolframalpha.com/input/?i=pi+*+%280.8mm%29%C2%B2+*+54mm+*+3
    def pump(self, direction, volume, speed=pump_max_speed):
        """moves the pump stepper

        direction is either FORWARD or BACKWARD
        volume is in mL
        speed is in mL/sec"""

        # Validation of inputs
        if direction != "FORWARD" and direction != "BACKWARD":
            print("ERROR! The direction command is not recognised")
            return

        if speed > self.pump_max_speed:
            speed = self.pump_max_speed
            print("WARNING! You requested speed is faster than the maximum safe speed")
            print("The speed of the motor is going to be limited")

        counter = 0

        nb_steps = self.pump_steps_per_ml * volume
        steps_per_second = speed * self.pump_steps_per_ml / 60

        # On linux, the minimal acceptable delay managed by the system is 0.1ms
        # see https://stackoverflow.com/questions/1133857/how-accurate-is-pythons-time-sleep
        # However we have a fixed delay of at least 2.5ms per step due to the library
        # Our maximum speed is thus about 400 pulses per second or 2 turn per second of the pump
        delay = max((1 / steps_per_second) - 0.0025, 0)

        # Depending on direction, select the right direction for the focus
        if direction == "FORWARD":
            direction = adafruit_motor.stepper.FORWARD

        if direction == "BACKWARD":
            direction = adafruit_motor.stepper.BACKWARD

        while True:
            # Actuate the focus for one double step in the right direction
            self.pump_stepper.onestep(
                direction=direction, style=adafruit_motor.stepper.DOUBLE
            )
            # Increment the counter
            counter += 1
            time.sleep(delay)
            ####################################################################
            # If counter reach the number of step, break
            if counter > nb_steps:
                # Release the focus steppers to stop power draw
                self.pump_stepper.release()
                break

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

        print("The stepper control thread has been started")
        while True:
            ############################################################################
            # Pump Event
            ############################################################################
            # If the command is "pump"
            if self.actuator_client.command == "pump":

                # Set the LEDs as Blue
                planktoscope.light.setRGB(0, 0, 255)

                # Get direction from the different received arguments
                direction = self.actuator_client.args.split(" ")[0]

                # Get delay (in between steps) from the different received arguments
                volume = float(self.actuator_client.args.split(" ")[1])

                # Get number of steps from the different received arguments
                speed = int(self.actuator_client.args.split(" ")[2])

                # Print status
                print("The pump has been started.")

                # Publish the status "Start" to via MQTT to Node-RED
                self.actuator_client.client.publish("actuator/pump/state", "Started")
                pump_thread = multiprocessing.Process(
                    target=self.pump, args=[direction, volume, speed]
                )
                pump_thread.start()

                ########################################################################
                while True:
                    if not pump_thread.is_alive():
                        # Thread has finished
                        # Print status
                        print("The pumping is done.")

                        # Change the command to not re-enter in this while loop
                        self.actuator_client.command = "wait"

                        # Publish the status "Done" to via MQTT to Node-RED
                        self.actuator_client.client.publish(
                            "actuator/pump/state", "Done"
                        )

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 0)

                        break

                    ####################################################################
                    # If a new received command isn't "pump", break this while loop
                    if not self.actuator_client.command.startswith("pump"):
                        pump_thread.terminate()
                        self.pump_stepper.release()

                        # Print status
                        print("The pump has been interrupted.")

                        # Publish the status "Interrompted" to via MQTT to Node-RED
                        self.actuator_client.client.publish(
                            "actuator/pump/state", "Interrupted"
                        )

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 0)

                        break

                    ####################################################################
                    # If a new received command is "pump" but args contains "stop" we stop!
                    if (
                        self.actuator_client.command == "pump"
                        and self.actuator_client.args == "stop"
                    ):
                        pump_thread.terminate()
                        self.pump_stepper.release()

                        # Print status
                        print("The pump has been stopped")

                        # Publish the status "Interrompted" to via MQTT to Node-RED
                        self.actuator_client.client.publish(
                            "actuator/pump/state", "Stopped"
                        )

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 0)

                        break

            ############################################################################
            # Focus Event
            ############################################################################

            # If the command is "focus"
            elif self.actuator_client.command == "focus":

                # Set the LEDs as Yellow
                planktoscope.light.setRGB(255, 255, 0)

                # Get direction from the different received arguments
                direction = self.actuator_client.args.split(" ")[0]

                # Get number of steps from the different received arguments
                distance = int(self.actuator_client.args.split(" ")[1])

                # Print status
                print("The focus has been started.")

                # Publish the status "Start" to via MQTT to Node-RED
                # self.actuator_client.client.publish("actuator/focus/state", "Start")

                # Starts the focus process
                focus_thread = multiprocessing.Process(
                    target=self.focus, args=(direction, distance)
                )
                focus_thread.start()
                ########################################################################
                while True:
                    if not focus_thread.is_alive():
                        # Thread has finished
                        # Print status
                        print("The focusing is done.")

                        # Change the command to not re-enter in this while loop
                        self.actuator_client.command = "wait"

                        # Publish the status "Done" to via MQTT to Node-RED
                        self.actuator_client.client.publish(
                            "actuator/focus/state", "Done"
                        )

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 0)

                        break

                    ####################################################################
                    # If a new received command isn't "focus", break this while loop
                    if not self.actuator_client.command.startswith("focus"):
                        # Kill the stepper thread
                        focus_thread.terminate()

                        # Release the focus steppers to stop power draw
                        self.focus_stepper.release()

                        # Print status
                        print("The stage has been interrupted.")

                        # Publish the status "Done" to via MQTT to Node-RED
                        self.actuator_client.client.publish(
                            "actuator/focus/state", "Interrupted"
                        )

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 0)

                        break

                    ####################################################################
                    # If a new received command is "focus" but args contains "stop" we stop!
                    if (
                        self.actuator_client.command == "focus"
                        and self.actuator_client.args == "stop"
                    ):
                        focus_thread.terminate()
                        self.focus_stepper.release()

                        # Print status
                        print("The focus has been stopped")

                        # Publish the status "Interrompted" to via MQTT to Node-RED
                        self.actuator_client.client.publish(
                            "actuator/focus/state", "Stopped"
                        )

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 0)

                        break


# This is called if this script is launched directly
if __name__ == "__main__":
    # Starts the stepper thread for actuators
    # This needs to be in a threading or multiprocessing wrapper
    stepper_thread = StepperProcess()
    stepper_thread.start()