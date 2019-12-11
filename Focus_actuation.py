from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

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
    
focus(1000,'up')
focus(1000,'down')
