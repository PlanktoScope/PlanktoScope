#!/usr/bin/env python

from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep
import sys

nb_step = int(sys.argv[1])
orientation = str(sys.argv[2])

kit = MotorKit()
stage = kit.stepper2
stage.release()

#0.25mm/step
#31um/microsteps
    
if orientation == 'up':
    for i in range(nb_step):
        stage.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
        sleep(0.001)

if orientation == 'down':
    for i in range(nb_step):
        stage.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
        sleep(0.001)
            
stage.release()
