#!/usr/bin/env python
# Turn on using this command line :
# python3.7 path/to/file/light.py on

# Turn off using this command line :
# python3.7 path/to/file/light.py off

# Library to send command over I2C for the light module on the fan
import smbus
import RPi.GPIO

# define the bus used to actuate the light module on the fan
bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x0D
rgb_effect_reg = 0x04
rgb_speed_reg = 0x05
rgb_color_reg = 0x06
rgb_off_reg = 0x07

################################################################################
# LEDs functions
################################################################################
def setRGB(R, G, B):
    """Update all LED at the same time"""
    bus.write_byte_data(DEVICE_ADDRESS, 0x00, 0xFF)
    bus.write_byte_data(DEVICE_ADDRESS, 0x01, R & 0xFF)
    bus.write_byte_data(DEVICE_ADDRESS, 0x02, G & 0xFF)
    bus.write_byte_data(DEVICE_ADDRESS, 0x03, B & 0xFF)

    # Update the I2C Bus in order to really update the LEDs new values
    cmd = "i2cdetect -y 1"
    subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)


def setRGBEffect(effect):
    """Choose an effect, 0-4

    0: Water light
    1: Breathing light
    2: Marquee
    3: Rainbow lights
    4: Colorful lights
    """

    if effect >= 0 and effect <= 4:
        bus.write_byte_data(DEVICE_ADDRESS, rgb_effect_reg, effect & 0xFF)


def setRGBSpeed(speed):
    """Set the effect speed, 1-3, 3 being the fastest speed"""
    if speed >= 1 and speed <= 3:
        bus.write_byte_data(DEVICE_ADDRESS, rgb_speed_reg, speed & 0xFF)


def setRGBColor(color):
    """Set the color of the water light and breathing light effect, 0-6

    0: Red
    1: Green (default)
    2: Blue
    3: Yellow
    4: Purple
    5: Cyan
    6: White
    """

    if color >= 0 and color <= 6:
        bus.write_byte_data(DEVICE_ADDRESS, rgb_color_reg, color & 0xFF)


def light(state):
    """Turn the LED on or off"""

    if state == "on":
        RPi.GPIO.output(21, RPi.GPIO.HIGH)
    if state == "off":
        RPi.GPIO.output(21, RPi.GPIO.LOW)


# This is called if this script is launched directly
if __name__ == "__main__":
    import RPi.GPIO as GPIO
    import sys

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(21, GPIO.OUT)

    state = str(sys.argv[1])

    light(state)
