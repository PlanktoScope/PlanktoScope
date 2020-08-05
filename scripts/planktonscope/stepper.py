# Libraries to control the steppers for focusing and pumping
import adafruit_motor
import adafruit_motorkit
import time
import json

# load config.json
with open("/home/pi/PlanktonScope/hardware.json", "r") as config_file:
    configuration = json.load(config_file)

reverse = False
focus_steps_per_mm = 40
pump_steps_per_ml = 100
# focus max speed is in mm/sec and is limited by the maximum number of pulses per second the Planktonscope can send
focus_max_speed = 0.5
# pump max speed is in ml/sec
pump_max_speed = 0.5

# parse the config data. If the key is absent, we are using the default value
reverse = configuration["hardware_config"].get("stepper_reverse", reverse)
focus_steps_per_mm = configuration["hardware_config"].get(
    "focus_steps_per_mm", focus_steps_per_mm
)
pump_steps_per_ml = configuration["hardware_config"].get(
    "pump_steps_per_ml", pump_steps_per_ml
)
focus_max_speed = configuration["hardware_config"].get(
    "focus_max_speed", focus_max_speed
)
pump_max_speed = configuration["hardware_config"].get("pump_max_speed", pump_max_speed)


# define the names for the 2 exsting steppers
kit = adafruit_motorkit.MotorKit()
if reverse:
    pump_stepper = kit.stepper2
    focus_stepper = kit.stepper1
else:
    pump_stepper = kit.stepper1
    focus_stepper = kit.stepper2

# Make sure the steppers are released and do not use any power
pump_stepper.release()
focus_stepper.release()


def focus(direction, distance, speed=focus_max_speed):
    """moves the focus stepper

    direction is either UP or DOWN
    distance is in mm
    speed is in mm/sec"""

    # Validation of inputs
    if direction != "UP" and direction != "DOWN":
        print("ERROR! The direction command is not recognised")
        return

    if distance > 90:
        print("ERROR! You are trying to move more than the stage physical size")
        return
    if speed > focus_max_speed:
        speed = focus_max_speed
        print("WARNING! You requested speed is faster than the maximum safe speed")
        print("The speed of the motor is going to be limited")

    counter = 0

    # We are going to use microsteps, so we need to multiply by 16 the steps number
    nb_steps = focus_steps_per_mm * distance * 16
    steps_per_second = speed * focus_steps_per_mm * 16

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
        focus_stepper.onestep(
            direction=direction, style=adafruit_motor.stepper.MICROSTEP
        )
        # Increment the counter
        counter += 1
        time.sleep(delay)
        ####################################################################
        # If counter reach the number of step, break
        if counter > nb_steps:
            # Release the focus steppers to stop power draw
            focus_stepper.release()
            break


# The pump max speed will be at about 400 full steps per second
# 0.65mL per seconds
# my pump is 0.3257 mL per round
def pump(direction, volume, speed=pump_max_speed):
    """moves the pump stepper

    direction is either FORWARD or BACKWARD
    volume is in mL
    speed is in mL/sec"""

    # Validation of inputs
    if direction != "FORWARD" and direction != "BACKWARD":
        print("ERROR! The direction command is not recognised")
        return

    if speed > pump_max_speed:
        speed = pump_max_speed
        print("WARNING! You requested speed is faster than the maximum safe speed")
        print("The speed of the motor is going to be limited")

    counter = 0

    nb_steps = pump_steps_per_ml * distance
    steps_per_second = speed * pump_steps_per_ml

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
        pump_stepper.onestep(direction=direction, style=adafruit_motor.stepper.DOUBLE)
        # Increment the counter
        counter += 1
        time.sleep(delay)
        ####################################################################
        # If counter reach the number of step, break
        if counter > nb_steps:
            # Release the focus steppers to stop power draw
            pump_stepper.release()
            break


# This is called if this script is launched directly
if __name__ == "__main__":
    import sys

    distance = int(sys.argv[1])
    direction = str(sys.argv[2])
    speed = float(sys.argv[1])
    focus(direction, distance, speed)
