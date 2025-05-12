# mypy: ignore-errors

import spidev
from loguru import logger

from motor.motor import Motor

"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2

class stepper:
    def __init__(self, pin, spi_bus, spi_device, size=0):
        """Initialize the stepper class

        Args:
            pin (int): pin of the motor
            spi_bus (int)
            spi_device (int)
            size (int): maximum number of steps of this stepper (aka stage size). Can be 0 if not applicable
        """
        self.init_spi(spi_bus, spi_device)
        self.__stepper = Motor(pin, self.__spi)
        self.stepper = self.__stepper
        self.__size = size
        self.__goal = 0
        self.__direction = ""
        self.__stepper.disable_motor()

    def init_spi(self, bus, device):
        spi = spidev.SpiDev()
        # Open(Bus, Device)
        spi.open(bus, device)
        # 1 MHZ
        spi.max_speed_hz = 1000000
        # 8 bits per word (32-bit word is broken into 4x 8-bit words)
        spi.bits_per_word = 8
        spi.loop = False
        # SPI Mode 3
        spi.mode = 3
        self.spi = spi
        self.__spi = spi

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

    def go(self, direction: int, distance: int):
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
