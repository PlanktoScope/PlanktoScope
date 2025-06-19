# mypy: ignore-errors

import time
from spidev import SpiDev

from gpiozero import DigitalOutputDevice

from . import registers as reg

"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2


class Motor:
    def __init__(self, pin: int, spi_bus: int, spi_device: int):
        self.enable = DigitalOutputDevice(pin, active_high=False)

        spi = SpiDev()
        spi.open(spi_bus, spi_device)
        # 1 MHZ
        spi.max_speed_hz = 1000000
        # 8 bits per word (32-bit word is broken into 4x 8-bit words)
        spi.bits_per_word = 8
        spi.loop = False
        # SPI Mode 3
        spi.mode = 3
        self.__spi = spi

        self.__goal = 0
        self.__direction = ""
        self.disable_motor()

    def enable_motor(self):
        self.enable.on()

    def disable_motor(self):
        self.enable.off()

    @property
    def ramp_AMAX(self):
        return self.__ramp_AMAX

    @ramp_AMAX.setter
    def ramp_AMAX(self, value: int):
        self.write(reg.AMAX, value)
        self.__ramp_AMAX = value

    @property
    def ramp_VMAX(self):
        return self.__ramp_VMAX

    @ramp_VMAX.setter
    def ramp_VMAX(self, value: int):
        self.write(reg.VMAX, value)
        self.__ramp_VMAX = value

    @property
    def ramp_DMAX(self):
        return self.__ramp_DMAX

    @ramp_DMAX.setter
    def ramp_DMAX(self, value: int):
        self.write(reg.DMAX, value)
        self.__ramp_DMAX = value

    def get_position(self) -> int:
        # Returns the current position of the motor relative to Home (0)

        current_position = self.read(reg.XACTUAL)

        # Convert 2's complement to get signed number
        current_position = self.twos_comp(current_position)

        return current_position

    def get_velocity(self) -> int:
        # Returns the current velocity of the motor (+ or -)

        current_velocity = self.read(reg.VACTUAL)

        # Convert 2's complement to get signed number
        # VACTUAL is valid for +-(2^23)-1, so 24 bits
        # 24 bits optional argument
        current_velocity = self.twos_comp(current_velocity, 24)

        return current_velocity

    def go_to(self, position: int):
        # Move to an absolute position relative to Home (0).

        self.position_mode()

        # Position range is from -2^31 to +(2^31)-1
        maximum_position = (2**31) - 1
        minimum_position = -(2**31)

        # Check if position is within bounds
        if position > maximum_position:
            position = maximum_position
            print("Maximum position reached! Stopped at max value.")
        elif position < minimum_position:
            position = minimum_position
            print("Minimum position reached! Stopped at min value.")

        self.write(reg.XTARGET, position)

    def move_velocity(self, dir: int, v_max: int = None, a_max: int = None):
        # Drive movor in velocity mode, positive or negative
        # If VMAX and AMAX are passed in, the ramp parameters won't
        # be overwritten.

        if v_max is not None:
            self.write(reg.VMAX, v_max)

        if a_max is not None:
            self.write(reg.AMAX, a_max)

        if dir == 0:
            velocity_mode = 1
            error = False
        elif dir == 1:
            velocity_mode = 2
            error = False
        else:
            print("Not a valid input! Please use 0 (left), or 1 (right).")
            error = True

        if not error:
            self.write(reg.RAMPMODE, velocity_mode)

    def stop_motor(self):
        # Stop all motion. Keep motor enabled.

        self.move_velocity(0, v_max=0)
        while self.get_velocity() != 0:
            time.sleep(0.01)
        self.hold_mode()
        self.ramp_VMAX = self.ramp_VMAX

    def hold_mode(self):
        self.write(reg.RAMPMODE, 3)

    def position_mode(self):
        self.write(reg.RAMPMODE, 0)

    def read(self, address: int) -> int:
        # Read data from the SPI bus.

        # Pre-populate data buffer with an empty array/list
        address_buffer = [0] * 5
        read_buffer = [0] * 5

        # Clear write bit
        address_buffer[0] = address & 0x7F

        self.__spi.xfer2(address_buffer)

        # It will look like [address, 0, 0, 0, 0]
        read_buffer = self.__spi.xfer2(address_buffer)

        # Parse data returned from SPI transfer/read
        value = read_buffer[1]
        value = value << 8
        value |= read_buffer[2]
        value = value << 8
        value |= read_buffer[3]
        value = value << 8
        value |= read_buffer[4]

        return value

    def write(self, address: int, data: int) -> int:
        # Write data to the SPI bus.

        # Pre-populate data buffer with an empty array/list
        write_buffer = [0] * 5

        # For write access, add 0x80 to address
        write_buffer[0] = address | 0x80

        write_buffer[1] = 0xFF & (data >> 24)
        write_buffer[2] = 0xFF & (data >> 16)
        write_buffer[3] = 0xFF & (data >> 8)
        write_buffer[4] = 0xFF & data

        return self.__spi.xfer2(write_buffer)

    def twos_comp(self, value: int, bits: int = 32) -> int:
        # if (value & (1 << (bits - 1))) != 0:
        #     signed_value = value - (1 << bits)
        # else:
        #     signed_value = value
        # return signed_value
        return (value - (1 << bits)) if ((value & (1 << (bits - 1))) != 0) else value

    @property
    def speed(self):
        return self.ramp_VMAX

    @speed.setter
    def speed(self, speed: int):
        """Change the stepper speed

        Args:
            speed (int): speed of the movement by the stepper, in microsteps unit/s
        """
        self.ramp_VMAX = int(speed)

    @property
    def acceleration(self):
        return self.ramp_AMAX

    @acceleration.setter
    def acceleration(self, acceleration: int):
        """Change the stepper acceleration

        Args:
            acceleration (int): acceleration reachable by the stepper, in microsteps unit/s²
        """
        self.ramp_AMAX = int(acceleration)

    @property
    def deceleration(self):
        return self.ramp_DMAX

    @deceleration.setter
    def deceleration(self, deceleration: int):
        """Change the stepper deceleration

        Args:
            deceleration (int): deceleration reachable by the stepper, in microsteps unit/s²
        """
        self.ramp_DMAX = int(deceleration)

    def at_goal(self):
        """Is the motor at its goal

        Returns:
            Bool: True if position and goal are identical
        """
        return self.get_position() == self.__goal

    def is_moving(self):
        """is the stepper in movement?

        Returns:
          Bool: True if the stepper is moving
        """
        return self.get_velocity() != 0

    def go(self, direction: int, distance: int):
        """move in the given direction for the given distance

        Args:
          direction: gives the movement direction
          distance:
        """

        self.__direction = direction
        if self.__direction == FORWARD:
            self.__goal = int(self.get_position() + distance)
        elif self.__direction == BACKWARD:
            self.__goal = int(self.get_position() - distance)
        else:
            raise ValueError(f'Unknown direction "{direction}".')
        self.enable_motor()
        self.go_to(self.__goal)

    def shutdown(self):
        """Shutdown everything ASAP"""
        self.stop_motor()
        self.disable_motor()
        self.__goal = self.get_position()

    def release(self):
        self.disable_motor()
