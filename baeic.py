#!/usr/bin/env python
# coding: utf-8

################################################################################
# A) Import the librairies needed to execute the script
################################################################################



#Time librairy in order to sleep when need
from time import sleep

#Picamera library to take images
from picamera import PiCamera

#Enable calculation of remaining duration and datetime
from datetime import datetime, timedelta

#Enable creation of new folders
import os


################################################################################
# B) Define the used pinout
################################################################################


#Affiliate pin to var for the LEDs
GREEN = LED(16)
RED = LED(12)
BLUE = LED(26)

#Affiliate pin to var for the RELAY
RELAY = LED(14)

bus= SMBus(1)

################################################################################
# C) Configuration file
################################################################################


camera = PiCamera()

camera.resolution = (3280, 2464)
camera.iso = 60

nb_frame=300

duration_loading=120 #(sec)
duration_flushing=20 #(sec)
duration_aeration=30 #(sec)

################################################################################
# D) Define simple sequence for I2C modules (Valves and pump)
################################################################################


def pump(state, verbose=True):

    sleep(0.2)

    if state is 'forward':
        # Stop pumping
        bus.write_byte(0x30, 1)
        sleep(1)
        feedback=bus.read_byte(0x30)
        if feedback == 1:
            if verbose is True:
                print("Pumping : Forward")

    if state is 'backward':
        # Stop pumping
        bus.write_byte(0x30, 2)
        sleep(1)
        feedback=bus.read_byte(0x30)
        if feedback == 2:
            if verbose is True:
                print("Pumping : Backward")

    if state is 'stop':
        # Stop pumping
        bus.write_byte(0x30, 0)
        sleep(1)
        feedback=bus.read_byte(0x30)
        if feedback == 0:
            if verbose is True:
                print("Pumping : Stop")

    if state is 'slow':
        # Start pumping
        bus.write_byte(0x30, 3)
        sleep(1)
        feedback=bus.read_byte(0x30)
        if feedback == 3:
            if verbose is True:
                print("Pumping : Slow")

    if state is 'medium':
        # Start pumping
        bus.write_byte(0x30, 5)
        sleep(1)
        feedback=bus.read_byte(0x30)
        if feedback == 5:
            if verbose is True:
                print("Pumping : Medium")

    if state is 'fast':
        # Start pumping
        bus.write_byte(0x30, 9)
        sleep(1)
        feedback=bus.read_byte(0x30)
        if feedback == 9:
            if verbose is True:
                print("Pumping : Fast")


################################################################################
# E) Define simple functions making the whole sequence
################################################################################


#First function to run in order to turn on the blue LED as well as the relay to make the I2C operationnal
def start():
    
    print("###############") 
    print("STARTING")
    print("###############")
    
    #Inform on the statut of the operation
    print("Starting : engaged")
    
    #turn the blue LED ON (even if it's written off here)
    BLUE.on()
    print("Led : Blue on")
    #turn the circuit ON (even if it's written off here)
    RELAY.off()
    print("Relay : Activated")
    
    for i in range(3):

        GREEN.on()
        print("Led : Green on")
        RED.on()
        print("Led : Red on")
        sleep(0.2)
        
        GREEN.off()
        print("Led : Green off")
        RED.off()
        print("Led : Red off")
        sleep(0.2)
    
    directory="/home/pi/Desktop/PlanktonScope_acquisition/"
    #create a directory if the directory doesn't exist yet
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    GREEN.on()
    
    #Inform on the statut of the operation
    print("Starting : done")



################################################################################

#The load will simply load a sample by pumping fast during a long period
def load():
    
    print("###############") 
    print("LOADING")
    print("###############")
    
    #Inform on the statut of the operation
    print("Loading : engaged")

    pump('fast', True)

    #wait to complete the loading process and print info on the terminal
    for i in range(duration_loading):
        print("Loading : "+str(i)+"/"+str(duration_loading))
        sleep(1) 
    
    #Inform on the statut of the operation
    print("Loading : done")

################################################################################

#image is very a basci way to take images
def image():
    
    print("###############") 
    print("IMAGING")
    print("###############")
    
    #Inform on the statut of the operation
    print("Imaging : engaged")
    
    #start the preview only during the acquisition
    camera.start_preview(fullscreen=False, window = (160, 0, 640, 480))
    #allow the camera to warm up
    sleep(2)
    
    for frame in range(nb_frame):
        
        #turn the green LED ON (even if it's written off here)
        GREEN.on()
        sleep(0.5)
        
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
        
        #get the time now
        time = datetime.now().strftime("%M_%S_%f")
        #create a filename from the date and the time
        filename="/home/pi/Desktop/PlanktonScope_acquisition/"+str(date_now)+"/"+str(hour_now)+"/"+str(time)+".jpg"

        #capture an image with the specified filename
        camera.capture(filename) 
        
        #wait to complete the imaging process and print info on the terminal
        print("Imaging : "+str(frame)+"/"+str(nb_frame))
        
        #turn the green LED OFF (even if it's written on here)
        GREEN.off()
        sleep(0.5)
 
    #stop the preview during the rest of the sequence
    camera.stop_preview()
    
    GREEN.on()
    pump('stop', True)
    
    #Inform on the statut of the operation
    print("Imaging : done")

################################################################################
# F) Execute the sequence
################################################################################


start()

while True: 
    init()
    load()
    flush()
    image()
    aeration()
    wait()
    
stop()

