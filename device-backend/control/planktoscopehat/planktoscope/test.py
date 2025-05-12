import os
import time

from loguru import logger

# from planktoscope.stepper import stepper
# import stepper
from stepper import stepper

"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2


class FocusProcess():
    focus_steps_per_mm = 40
    # focus max speed is in mm/sec and is limited by the maximum number of pulses per second the PlanktoScope can send
    focus_max_speed = 5

    def __init__(self):
        super(FocusProcess, self).__init__()
        logger.info("Initialising the focus process")

        self.focus_started = False


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

foo = FocusProcess()

# print("2147565568")

# drv_status = 2147565568

# print()

# bytes = drv_status.to_bytes(32)

# print(drv_status&4 != 0)

#print(bytes(drv_status))

while True:
    drv_status = foo.focus_stepper.stepper.read(0x6F)
#     # 2147565568


    #     print(drv_status.to)

    #     # print(drv_status[0])

    # DRVSTATUS
    addr = 0x6F
    # "DRVSTATUS"
    reg_map = [
        # name                  position,  mask    type
        ["stst",                31,        0x1,    bool,   None, ""],
        ["olb",                 30,        0x1,    bool,   None, ""],
        ["ola",                 29,        0x1,    bool,   None, ""],
        ["s2gb",                28,        0x1,    bool,   None, ""],
        ["s2ga",                27,        0x1,    bool,   None, ""],
        ["otpw",                26,        0x1,    bool,   None, ""],
        ["ot",                  25,        0x1,    bool,   None, ""],
        ["stallguard",          24,        0x1,    bool,   None, ""],
        ["cs_actual",           16,        0x1F,   int,    None, ""],
        ["fsactive",            15,        0x1,    bool,   None, ""],
        ["stealth",             14,        0x1,    bool,   None, ""],
        ["s2vsb",               13,        0x1,    bool,   None, ""],
        ["s2vsa",               12,        0x1,    bool,   None, ""],
        ["sgresult",            0,         0x3FF,  int,    None, ""]
    ]

    obj = {}
    for reg in reg_map:
        name, pos, mask, reg_class, _, _ = reg
        value = drv_status >> pos & mask
        obj[name] = reg_class(value)

    # SGRESULT
    reg_map = [
        ["sgresult",            0,  0xFFFFF, int, None, ""]
    ]

    obj2 = {}
    for reg in reg_map:
        name, pos, mask, reg_class, _, _ = reg
        value = obj["sgresult"] >> pos & mask
        obj2[name] = reg_class(value)

    print(obj2)
