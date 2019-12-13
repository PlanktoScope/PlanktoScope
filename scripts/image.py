#!/usr/bin/env python

#Imaging a volume with a flowrate
#in folder named "/home/pi/PlanktonScope/acquisitions/sample_project/sample_id/acq_id"
#python3.7 $HOME/PlanktonScope/scripts/image.py tara_pacific sample_project sample_id acq_id volume flowrate

import time
from time import sleep
from picamera import PiCamera
from datetime import datetime, timedelta
import os
import sys

in_path = str(sys.argv[1])

#[t] : ex:tara_pacific
sample_project = str(sys.argv[2])

#[t] : unique identifier
sample_id = str(sys.argv[3])

#[t] : unique identifier
acq_id = str(sys.argv[4])

#[i] : ex:24ml
volume = int(sys.argv[5])

#[f] : ex:3.2ml/min
flowrate = float(sys.argv[6])

warm_up_duration=3

duration = (volume/flowrate)*60 - warm_up_duration

max_fps = 0.7

nb_frame = int(duration/max_fps)

path= in_path+sample_project+"/"+sample_id+"/"+acq_id+"/"
    
if not os.path.exists(path):
    os.makedirs(path)
    
camera = PiCamera()

camera.resolution = (3280, 2464)
camera.iso = 60


def image(nb_frame, path):
    
    sleep(3)
    
    for frame in range(nb_frame):
        
        time = datetime.now().timestamp()
        
        filename=path+"/"+str(time)+".jpg"

        camera.capture(filename) 
        
        print(time)
        sleep(0.1)
 

image(nb_frame, path)
