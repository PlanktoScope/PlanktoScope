from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep
kit = MotorKit()

stage = kit.stepper1

stage.release()

def focus_actuation(steps,orientation):  

    stage.release()
    
    if orientation == 'FORWARD':
        for i in range(steps):
            stage.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
            sleep(0.001)
            
    if orientation == 'BACKWARD':
        for i in range(steps):
            stage.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
            sleep(0.001)
            
    stage.release()
    
focus_actuation(1000,'FORWARD')
focus_actuation(1000,'BACKWARD')
