.. _install:

============
Installation
============

.. currentmodule:: picamera


.. _raspbian_install:

Raspbian installation
=====================

If you are using the `Raspbian`_ distro, it is best to install picamera using
the system's package manager: apt. This will ensure that picamera is easy to
keep up to date, and easy to remove should you wish to do so. It will also make
picamera available for all users on the system. To install picamera using apt
simply::

A) Import the librairies needed to execute the script
=======================================================

If you are using the `Raspbian`_ distro, it is best to install picamera using
the system's package manager: apt. This will ensure that picamera is easy to
keep up to date, and easy to remove should you wish to do so. It will also make
picamera available for all users on the system. To install picamera using apt
simply::

  from gpiozero import LED
  import smbus2 as smbus
  from time import sleep
  from picamera import PiCamera
  from datetime import datetime, timedelta
  import os


B) Define the used pinout
=========================

  #Affiliate pin to var for the LEDs
  GREEN = LED(16)
  RED = LED(12)
  BLUE = LED(26)

  #Affiliate pin to var for the RELAY
  RELAY = LED(14)


C) Configuration file
=====================

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

D) Define simple sequence for I2C modules (Valves and pump)
===========================================================

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
