from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

import sys

vol = int(sys.argv[1])
flowrate = int(sys.argv[2])
dir = str(sys.argv[3])

kit = MotorKit()

pump_stepper = kit.stepper2

pump_stepper.release()

def pump(vol, flowrate, dir):
    
    if dir == "foward":
        dir=stepper.FORWARD
    if dir == "backward":
        dir=stepper.BACKWARD
        
    nb_step=vol*507 #if sleep(0.05) in between 2 steps
    #35000steps for 69g
    
    #nb_step=vol*460 if sleep(0) in between 2 steps
    duration=(vol*60)/flowrate
    
    delay=(duration/nb_step)-0.005
    
    for i in range(nb_step):
        pump_stepper.onestep(direction=dir, style=stepper.DOUBLE)
        sleep(delay)
        
    sleep(1)
    pump_stepper.release()
    
#volume, flowrate (from 0 to 20), direction (foward or backward)
pump(vol, flowrate, dir)

