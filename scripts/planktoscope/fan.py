#!/usr/bin/python
import smbus
import sys

state = str(sys.argv[1])

bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x0d

def fan(state):
    if state == "false":
        bus.write_byte_data(DEVICE_ADDRESS, 0x08, 0x00)
        bus.write_byte_data(DEVICE_ADDRESS, 0x08, 0x00)
    if state == "true":
        bus.write_byte_data(DEVICE_ADDRESS, 0x08, 0x01)
        bus.write_byte_data(DEVICE_ADDRESS, 0x08, 0x01)

fan(state)