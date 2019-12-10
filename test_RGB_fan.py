#!/usr/bin/python
import smbus
from time import sleep

bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x0d

def led_on(LED, R,G,B):
    bus.write_byte_data(DEVICE_ADDRESS, 0x00, LED)
    bus.write_byte_data(DEVICE_ADDRESS, 0x01, R)
    bus.write_byte_data(DEVICE_ADDRESS, 0x02, G)
    bus.write_byte_data(DEVICE_ADDRESS, 0x03, B)

def led_off():
    bus.write_byte_data(DEVICE_ADDRESS, 0x07, 0x00)

def breathe_slow():
    bus.write_byte_data(DEVICE_ADDRESS, 0x04, 0x01)
    
def breathe_fast():
    bus.write_byte_data(DEVICE_ADDRESS, 0x04, 0x03)

led_off()
led_on(0, 25,58,255)
led_on(1, 25,58,255)
led_on(2, 25,58,255)
sleep(5)
breathe_slow()
sleep(5)
led_off()



