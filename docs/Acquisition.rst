.. _install:

============
Acquisition
============

  #!/usr/bin/env python
  # coding: utf-8

  ################################################################################
  # A) Import the librairies needed to execute the script
  ################################################################################


  #Activate pinout to control the LEDs and the RELAY
  from gpiozero import LED

  #Allow to access the I2C BUS from the Raspberry Pi
  import smbus2 as smbus

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


  ################################################################################
  # C) Configuration file
  ################################################################################


  camera = PiCamera()

  camera.resolution = (2592, 1944)
  camera.iso = 60
  camera.exposure_mode = 'off'
  camera.shutter_speed = 100
  camera.awb_mode = 'off'
  camera.awb_gains = (2,1)

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


  def valve(state, verbose=True):

      sleep(0.2)

      if state is 'open_all':
          bus.write_byte(0x20, 1)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 1:
              if verbose:
                  print("Valve : All open")

      if state is 'close_all':
          bus.write_byte(0x20, 0)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 0:
              if verbose:
                  print("Valve : All closed")


      if state is 'open_in_sample':
          bus.write_byte(0x20, 2)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 2:
              if verbose:
                  print("Valve : In sample open")

      if state is 'close_in_sample':
          bus.write_byte(0x20, 3)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 3:
              if verbose:
                  print("Valve : In sample closed")

      if state is 'open_in_air':
          bus.write_byte(0x20, 4)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 4:
              if verbose:
                  print("Valve : In air open") 

      if state is 'close_in_air':
          bus.write_byte(0x20, 5)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 5:
              if verbose:
                  print("Valve : In air closed")

      if state is 'open_in_bleach':
          bus.write_byte(0x20, 6)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 6:
              if verbose:
                  print("Valve : In bleach open")  

      if state is 'close_in_bleach':
          bus.write_byte(0x20, 7)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 7:
              if verbose:
                  print("Valve : In bleach closed")

      if state is 'open_out_bleach':
          bus.write_byte(0x20, 8)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 8:
              if verbose:
                  print("Valve : Out bleach open")    

      if state is 'close_out_bleach':
          bus.write_byte(0x20, 9)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 9:
              if verbose:
                  print("Valve : Out bleach closed")

      if state is 'open_out_sample':
          bus.write_byte(0x20, 10)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 10:
              if verbose: 
                  print("Valve : Out sample open")    

      if state is 'close_out_sample':
          bus.write_byte(0x20, 11)
          sleep(1)
          feedback=bus.read_byte(0x20)
          if feedback == 11:
              if verbose: 
                  print("Valve : Out sample closed")


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
      BLUE.off()
      print("Led : Blue on")
      #turn the circuit ON (even if it's written off here)
      RELAY.off()
      print("Relay : Activated")

      for i in range(3):
          GREEN.off()
          print("Led : Green on")
          RED.off()
          print("Led : Red on")
          sleep(0.1)

          GREEN.on()
          print("Led : Green off")
          RED.on()
          print("Led : Red off")
          sleep(0.1)


      directory="/pi/home/Desktop/PlanktonScope_acquisition/"
      #create a directory if the directory doesn't exist yet
      if not os.path.exists(directory):
          os.makedirs(directory)

      GREEN.off()

      #Inform on the statut of the operation
      print("Starting : done")


  ################################################################################

  #This function will prepare the pump and the valves to realize the loading operation
  def init():

      print("###############") 
      print("INITIALIZING")
      print("###############")

      #Inform on the statut of the operation
      print("Initializing : engaged")

      pump('forward', True)

      pump('stop', True)

      valve('open_in_sample', True)
      valve('open_out_sample', True)

      valve('close_in_air', True)

      valve('close_in_bleach', True)
      valve('close_out_bleach', True)

      #Inform on the statut of the operation
      print("Initializing : done")


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

  #flush will create some valving sequence to remove potential air trapped in the tubes
  def flush():

      print("###############") 
      print("FLUSHING")
      print("###############")

      #Inform on the statut of the operation
      print("Flushing : engaged")

      valve('close_in_sample', True)
      valve('open_in_sample', True)

      valve('close_in_sample', True)
      valve('open_in_sample', True)

      pump('slow', True)

      #wait to complete the flushing process and print info on the terminal
      for i in range(duration_flushing):
          print("Flushing : "+str(i)+"/"+str(duration_flushing))
          sleep(1) 

      #Inform on the statut of the operation
      print("Flushing : done")


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
          GREEN.off()
          sleep(0.5)

          #get the actual date
          date = datetime.now().strftime("%m_%d_%Y")
          directory="/pi/home/Desktop/PlanktonScope_acquisition/"+str(date)

          #create a directory if the directory doesn't exist yet
          if not os.path.exists(directory):
              os.makedirs(directory)

          #get the time now
          time = datetime.now().strftime("%H_%M_%S_%f")
          #create a filename from the date and the time
          filename="/pi/home/Desktop/PlanktonScope_acquisition/"+str(date)+"/"+str(time)+".jpg"

          #capture an image with the specified filename
          camera.capture(filename) 

          #wait to complete the imaging process and print info on the terminal
          print("Imaging : "+str(frame)+"/"+str(nb_frame))

          #turn the green LED OFF (even if it's written on here)
          GREEN.on()
          sleep(0.5)

      #stop the preview during the rest of the sequence
      camera.stop_preview()

      GREEN.off()
      pump('stop', True)

      #Inform on the statut of the operation
      print("Imaging : done")


  ################################################################################

  #aeration will remove the liquid from the tube and replace it by air
  def aeration():

      print("###############") 
      print("AERATION")
      print("###############")  

      #Inform on the statut of the operation
      print("Aeration : engaged")

      #remove liquid from tubes   
      pump('stop', True)

      valve('close_all', True)

      valve('open_in_air', True)
      valve('open_out_sample', True)

      pump('medium', True)    

      #wait to complete the aeration process and print info on the terminal
      for i in range(duration_aeration):
          print("Aerating : "+str(i)+"/"+str(duration_aeration))
          sleep(1) 

      pump('stop', True)

      #Inform on the statut of the operation
      print("Aeration : done")


  ################################################################################

  #wait will make the pi sleep until the next hour
  def wait():

      print("###############") 
      print("WAITING")
      print("###############")

      #Inform on the statut of the operation
      print("Waiting : engaged")

      # Calculate the delay to the start of the next hour
      next_hour = (datetime.now() + timedelta(hour=1)).replace(
      minute=0, second=0, microsecond=0)
      delay = (next_hour - datetime.now()).seconds

      #wait to complete the waiting process and print info on the terminal
      for i in range(delay):
          print("Waiting : "+str(i)+"/"+str(delay))
          sleep(1) 

      #Inform on the statut of the operation
      print("Waiting : done")


  ################################################################################

  #stop will turn off the green LED and turn on the red one
  def stop():

      GREEN.on()
      print("Led : Green off")
      RED.off()
      print("Led : Red on")

      #Inform on the statut of the operation
      print("The sequence is done.")


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
