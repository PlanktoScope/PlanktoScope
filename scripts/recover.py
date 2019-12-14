#!/usr/bin/env python
#recover the hardware after a brutal killing

from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

kit = MotorKit()

stage = kit.stepper1
pump_stepper = kit.stepper2

#release the steppers after killing
stage.release()
pump_stepper.release()

