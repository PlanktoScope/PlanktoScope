#!/usr/bin/python
import smbus
from time import sleep

bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x0d


def fan_toggle():
    bus.write_byte_data(DEVICE_ADDRESS, 0x08, 0x01)

fan_toggle()



