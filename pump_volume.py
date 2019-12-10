from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

kit = MotorKit()

pump = kit.stepper2

pump.release()



def pump_volume(vol):
    nb_step=vol*507 #35000steps for 69g with sleep(0.05) in between 2 steps
    for i in range(nb_step):
        pump.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
        sleep(0.05)
    pump.release()
    
    
pump_volume(5)
