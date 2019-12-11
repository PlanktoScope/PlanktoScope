#!/usr/bin/env python
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

from thread2 import Thread
import sys

nb_step = int(sys.argv[1])
orientation = str(sys.argv[2])
toogler = str(sys.argv[3])


#Execute a python cmd with the previous defined variables from php


kit = MotorKit()

stage = kit.stepper1

stage.release()

def focus(steps,orientation):
    #0.25mm/step
    #31um/microsteps

    stage.release()
    
    if orientation == 'up':
        for i in range(steps):
            stage.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
            sleep(0.001)
            
    if orientation == 'down':
        for i in range(steps):
            stage.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
            sleep(0.001)
            
    stage.release()

focus_thread = Thread(target = focus, name = 'focus_thread', args =(nb_step, orientation) )
 
if toogler == "ON":
        
    focus_thread.start()
    focus_thread.isAlive()
    
if toogler == "OFF":
        
    focus_thread.terminate()
    focus_thread.join()
    focus_thread.isAlive()
    stage.release()

