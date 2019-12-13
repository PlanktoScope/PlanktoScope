#!/usr/bin/env python

#Imaging a volume of 24ml with a flowrate of 3.2ml/min 
#in folder named "/home/pi/Desktop/tara_pacific/20200226/142632/"
#python3.7 path/to/file/image.py tara_pacific 20200226 142632 24 3.2

import time
from time import sleep
from picamera import PiCamera
from datetime import datetime, timedelta
import os
import sys

#[t] : ex:tara_pacific
sample_project = str(sys.argv[1])

#[f] : ISO8601 YYYYMMJJ UTC
sample_date = str(sys.argv[2])

#[f] : ISO8601 HHMMSS UTC
sample_time = str(sys.argv[3])

#[i] : ex:24ml
volume = int(sys.argv[4])

#[f] : ex:3.2ml/min
flowrate = float(sys.argv[5])

warm_up_duration=3

duration = (volume/flowrate)*60 - warm_up_duration

max_fps = 0.7

nb_frame = int(duration/max_fps)

path= "/home/pi/Desktop/"+sample_project+"/"+sample_date+"/"+sample_time+"/"
    
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

