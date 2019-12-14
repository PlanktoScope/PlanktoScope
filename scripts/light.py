#!/usr/bin/env python
#Turn on using this command line : 
#python3.7 path/to/file/light.py on

#Turn off using this command line : 
#python3.7 path/to/file/light.py off

import RPi.GPIO as GPIO
import sys


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21,GPIO.OUT)

state = str(sys.argv[1])


def light(state):
    
    if state == "true":
        GPIO.output(21,GPIO.HIGH)
    if state == "false":
        GPIO.output(21,GPIO.LOW)
        
light(state)
