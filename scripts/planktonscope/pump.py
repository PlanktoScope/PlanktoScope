#!/usr/bin/env python

#Strating pumping foward a vol of 24ml with a flowrate of 3.2ml/min, use this command line : 
#python3.7 path/to/file/pump.py 24 3.2 foward

from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

import sys

volume = int(sys.argv[1])
flowrate = float(sys.argv[2])
action = str(sys.argv[3])

kit = MotorKit()

pump_stepper = kit.stepper1

pump_stepper.release()

def pump(volume, flowrate, action):
    
    if action == "foward":
        action=stepper.BACKWARD
    if action == "backward":
        action=stepper.FORWARD
        
    nb_step=volume*507 #if sleep(0.05) in between 2 steps
    #35000steps for 69g
    
    #nb_step=vol*460 if sleep(0) in between 2 steps
    duration=(volume*60)/flowrate
    
    delay=(duration/nb_step)-0.005
    
    for i in range(nb_step):
        pump_stepper.onestep(direction=action, style=stepper.DOUBLE)
        sleep(delay)
        
    sleep(1)
    pump_stepper.release()
    
#volume, flowrate (from 0 to 20), direction (foward or backward)
pump(volume, flowrate, action)

