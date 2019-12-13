#!/usr/bin/env python
import time
from time import sleep
from picamera import PiCamera
from datetime import datetime, timedelta
import os
import sys


#[t] : ex:tara_pacific
sample_project = int(sys.argv[X])

#[f] : ISO8601 YYYYMMJJ UTC
sample_date = float(sys.argv[X])

#[f] : ISO8601 HHMMSS UTC
sample_time = float(sys.argv[X])

#[i] : ex:24ml
volume = int(sys.argv[X])

#[f] : ex:3ml/min
flowrate = float(sys.argv[X])

duration = (volume/flowrate)*60

max_fps = 0.62

nb_frame = float(duration/max_fps)

path= "/home/pi/Desktop/"+str(sample_project)+"/"+str(sample_date)+"/"+str(sample_time)+"/"
    
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
