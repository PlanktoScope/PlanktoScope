from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep
from datetime import datetime
import time

kit = MotorKit()

pump = kit.stepper2

pump.release()



def pump_volume(vol, flowrate):
    nb_step=vol*507 #if sleep(0.05) in between 2 steps
    #35000steps for 69g 
    #nb_step=vol*460 if sleep(0) in between 2 steps
    duration=(vol*60)/flowrate
    delay=(duration/nb_step)-0.005
    #flowrate is about 2.2ml/min
    for i in range(nb_step):
        pump.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
        sleep(delay)
    print(delay)
    sleep(1)
    pump.release()
    
volume=1

flowrate=1 #20 is the max

start = time.time()

pump_volume(volume, flowrate)

end = time.time()

duration = end-start

print(duration)


