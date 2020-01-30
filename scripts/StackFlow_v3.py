#!/usr/bin/env python
# coding: utf-8

################################################################################
# A) Import the librairies needed to execute the script
################################################################################
#Activate pinout to control the LEDs and the RELAY
from gpiozero import LED
#Allow to access the I2C BUS from the Raspberry Pi
import smbus
#Time librairy in order to sleep when need
from time import sleep
#Picamera library to take images
from picamera import PiCamera
#Enable calculation of remaining duration and datetime
from datetime import datetime, timedelta
#Enable creation of new folders
import os
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

kit = MotorKit()
pump_stepper = kit.stepper1
pump_stepper.release()


################################################################################
# C) Configuration file
################################################################################


camera = PiCamera()
camera.resolution = (3280, 2464)
camera.iso = 60
sleep(3)
camera.shutter_speed = 300
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
nb_frame=2000

pump_stepper.release()
################################################################################
# E) Define simple functions making the whole sequence
###

################################################################################

    
print("###############") 
print("IMAGING")
print("###############")

#Inform on the statut of the operation
print("Imaging : engaged")
#start the preview only during the acquisition
camera.start_preview(fullscreen=False, window = (160, 0, 640, 480))


#get the actual date
date_now = datetime.now().strftime("%m_%d_%Y")
day_now="/home/pi/Desktop/PlanktonScope_acquisition/"+str(date_now)

#create a directory if the directory doesn't exist yet
if not os.path.exists(day_now):
    os.makedirs(day_now)
    
#get the actual date
hour_now = datetime.now().strftime("%H")
hour="/home/pi/Desktop/PlanktonScope_acquisition/"+str(date_now)+"/"+str(hour_now)

#create a directory if the directory doesn't exist yet
if not os.path.exists(hour):
    os.makedirs(hour)
    

#allow the camera to warm up

for i in range(200):
    pump_stepper.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    sleep(0.01)
    
for frame in range(nb_frame):
    
    #get the time now
    time = datetime.now().strftime("%M_%S_%f")
    #create a filename from the date and the time
    filename="/home/pi/Desktop/PlanktonScope_acquisition/"+str(date_now)+"/"+str(hour_now)+"/"+str(time)+".jpg"

    #capture an image with the specified filename
    camera.capture(filename)
    
    #wait to complete the imaging process and print info on the terminal
    print("Imaging : "+str(frame)+"/"+str(nb_frame))
    
    for i in range(10):
        pump_stepper.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
        sleep(0.01)
    sleep(0.5)
        

#stop the preview during the rest of the sequence
camera.stop_preview()
pump_stepper.release()

#Inform on the statut of the operation
print("Imaging : done")


################################################################################

#################################################
# F) Execute the sequence
################################################################################
