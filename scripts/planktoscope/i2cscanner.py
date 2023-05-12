# Copyright (C) 2023 Romain Bazile
#
# This file is part of PlanktoScope.
#
# PlanktoScope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PlanktoScope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PlanktoScope.  If not, see <http://www.gnu.org/licenses/>.
import smbus2 as smbus
from loguru import logger


def scan(address):
    logger.info(f"[I2C] Trying to find a device at {address}")
    if 0x08 <= address <= 0x77:
        with smbus.SMBus(1) as bus:
            try:
                bus.write_quick(address)
            except IOError as e:
                logger.info(f"[I2C] No device at {address}")
                return False
            else:
                logger.info(f"[I2C] Device found at {address}")
                return True
    else:
        logger.info(f"[I2C] {address} must be between 0x08 and 0x77")
        return False
