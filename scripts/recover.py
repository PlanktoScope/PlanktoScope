#!/usr/bin/env python
#recover the hardware after a brutal killing

from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep
import RPi.GPIO as GPIO

kit = MotorKit()

stage = kit.stepper1
pump_stepper = kit.stepper2

#release the steppers after killing
stage.release()
pump_stepper.release()

#turn off LED after killing
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21,GPIO.OUT)
GPIO.output(21,GPIO.LOW)
