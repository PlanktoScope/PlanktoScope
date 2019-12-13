#!/usr/bin/env python
import RPi.GPIO as GPIO
import sys


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21,GPIO.OUT)

state = int(sys.argv[1])


def light(state):
    
    if state == "on":
        GPIO.output(21,GPIO.HIGH)
    if state == "off":
        GPIO.output(21,GPIO.LOW)
        
light(state)
