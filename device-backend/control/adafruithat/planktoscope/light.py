#!/usr/bin/env python
# Copyright (C) 2021 Romain Bazile
# 
# This file is part of the PlanktoScope software.
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

# Turn on using this command line :
# python3.7 path/to/file/light.py on

# Turn off using this command line :
# python3.7 path/to/file/light.py off

# Logger library compatible with multiprocessing
from loguru import logger

import subprocess  # nosec

# Library to send command over I2C for the light module on the fan
import smbus2 as smbus

import enum

DEVICE_ADDRESS = 0x0D


@enum.unique
class Register(enum.IntEnum):
    led_select = 0x00
    red = 0x01
    green = 0x02
    blue = 0x03
    rgb_effect = 0x04
    rgb_speed = 0x05
    rgb_color = 0x06
    rgb_off = 0x07


@enum.unique
class Effect(enum.IntEnum):
    Water = 0
    Breathing = 1
    Marquee = 2
    Rainbow = 3
    Colorful = 4


@enum.unique
class EffectColor(enum.IntEnum):
    Red = 0
    Green = 1
    Blue = 2
    Yellow = 3
    Purple = 4
    Cyan = 5
    White = 6


def i2c_update():
    # Update the I2C Bus in order to really update the LEDs new values
    subprocess.Popen("i2cdetect -y 1".split(), stdout=subprocess.PIPE)  # nosec


################################################################################
# LEDs functions
################################################################################
def setRGB(R, G, B):
    """Update all LED at the same time"""
    try:
        with smbus.SMBus(1) as bus:
            bus.write_byte_data(DEVICE_ADDRESS, Register.led_select, 0xFF)
            bus.write_byte_data(
                DEVICE_ADDRESS, Register.led_select, 0xFF
            )  # 0xFF write to all LEDs, 0x01/0x02/0x03 to choose first, second or third LED
            bus.write_byte_data(DEVICE_ADDRESS, Register.red, R & 0xFF)
            bus.write_byte_data(DEVICE_ADDRESS, Register.green, G & 0xFF)
            bus.write_byte_data(DEVICE_ADDRESS, Register.blue, B & 0xFF)
        i2c_update()
    except Exception as e:
        logger.exception(f"An Exception has occured in the light library at {e}")


def setRGBOff():
    """Turn off the RGB LED"""
    try:
        with smbus.SMBus(1) as bus:
            bus.write_byte_data(DEVICE_ADDRESS, Register.rgb_off, 0x00)
        i2c_update()
    except Exception as e:
        logger.exception(f"An Exception has occured in the light library at {e}")


def setRGBEffect(bus, effect):
    """Choose an effect, type Effect

    Effect.Water: Rotating color between LEDs (color has an effect)
    Effect.Breathing: Breathing color effect
    Effect.Marquee: Flashing color transition between all LEDs
    Effect.Rainbow: Smooth color transition between all LEDs
    Effect.Colorful: Colorful transition separately between all LEDs
    """
    if effect in Effect:
        try:
            bus.write_byte_data(DEVICE_ADDRESS, Register.rgb_effect, effect & 0xFF)
        except Exception as e:
            logger.exception(f"An Exception has occured in the light library at {e}")


def setRGBSpeed(bus, speed):
    """Set the effect speed, 1-3, 3 being the fastest speed"""
    if 1 <= speed <= 3:
        try:
            bus.write_byte_data(DEVICE_ADDRESS, Register.rgb_speed, speed & 0xFF)
        except Exception as e:
            logger.exception(f"An Exception has occured in the light library at {e}")


def setRGBColor(bus, color):
    """Set the color of the water light and breathing light effect, of type EffectColor

    EffectColor.Red, EffectColor.Green (default), EffectColor.Blue, EffectColor.Yellow,
    EffectColor.Purple, EffectColor.Cyan, EffectColor.White
    """
    if color in EffectColor:
        try:
            bus.write_byte_data(DEVICE_ADDRESS, Register.rgb_color, color & 0xFF)
        except Exception as e:
            logger.exception(f"An Exception has occured in the light library at {e}")


def ready():
    with smbus.SMBus(1) as bus:
        setRGBColor(bus, EffectColor.Blue)
        setRGBSpeed(bus, 1)
        setRGBEffect(bus, Effect.Breathing)
        i2c_update()


def error():
    with smbus.SMBus(1) as bus:
        setRGBColor(bus, EffectColor.Red)
        setRGBSpeed(bus, 3)
        setRGBEffect(bus, Effect.Water)
        i2c_update()


def interrupted():
    with smbus.SMBus(1) as bus:
        setRGBColor(bus, EffectColor.Yellow)
        setRGBSpeed(bus, 3)
        setRGBEffect(bus, Effect.Water)
        i2c_update()


def pumping():
    with smbus.SMBus(1) as bus:
        setRGBColor(bus, EffectColor.Blue)
        setRGBSpeed(bus, 3)
        setRGBEffect(bus, Effect.Water)
        i2c_update()


def focusing():
    with smbus.SMBus(1) as bus:
        setRGBColor(bus, EffectColor.Purple)
        setRGBSpeed(bus, 3)
        setRGBEffect(bus, Effect.Water)
        i2c_update()


def imaging():
    with smbus.SMBus(1) as bus:
        setRGBColor(bus, EffectColor.White)
        setRGBSpeed(bus, 1)
        setRGBEffect(bus, Effect.Breathing)
        i2c_update()


def segmenting():
    with smbus.SMBus(1) as bus:
        setRGBColor(bus, EffectColor.Purple)
        setRGBSpeed(bus, 1)
        setRGBEffect(bus, Effect.Breathing)
        i2c_update()


# This is called if this script is launched directly
if __name__ == "__main__":
    # TODO This should be a test suite for this library
    import time

    print("ready")
    ready()
    time.sleep(5)
    print("error")
    error()
    time.sleep(5)
    print("pumping")
    pumping()
    time.sleep(5)
    print("focusing")
    focusing()
    time.sleep(5)
    print("imaging")
    imaging()
    time.sleep(5)
    print("segmenting")
    segmenting()
    time.sleep(5)
    print("with i2c_update now!")
    print("ready")
    ready()
    i2c_update()
    time.sleep(5)
    print("error")
    error()
    i2c_update()
    time.sleep(5)
    print("pumping")
    pumping()
    i2c_update()
    time.sleep(5)
    print("focusing")
    focusing()
    i2c_update()
    time.sleep(5)
    print("imaging")
    imaging()
    i2c_update()
    time.sleep(5)
    print("segmenting")
    segmenting()
    i2c_update()
    time.sleep(5)

    with smbus.SMBus(1) as bus:
        setRGBSpeed(bus, 3)
    for effect in Effect:
        print(effect.name)
        with smbus.SMBus(1) as bus:
            setRGBEffect(bus, effect)
        time.sleep(2)
    with smbus.SMBus(1) as bus:
        setRGBEffect(bus, Effect.Breathing)
    for color in EffectColor:
        print(color.name)
        with smbus.SMBus(1) as bus:
            setRGBColor(bus, color)
        time.sleep(2)

    setRGBOff()
