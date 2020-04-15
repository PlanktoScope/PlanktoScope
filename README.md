PlanktonScope Installation
==========================

*************************************
Install Raspbian on your Raspberry Pi
*************************************

Download the image
==================

Download the .zip file of Raspbian Buster with desktop from the Raspberry Pi website Downloads page.

Writing an image to the SD card

Download the latest version of balenaEtcher and install it.

Connect an SD card reader with the micro SD card inside.

Open balenaEtcher and select from your hard drive the Raspberry Pi .zip file you wish to write to the SD card.

Select the SD card you wish to write your image to.

Review your selections and click 'Flash!' to begin writing data to the SD card.

Prepare your Raspberry Pi
-------------------------
`Getting Started with your Raspberry Pi <https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/>`_

Plug the SD Card in your Raspberry Pi

Connect your Pi to a screen, mouse, keyboard and power 

Finish the setup

Make sure you have access to internet and update/upgrade your fresh raspbian

Update your Pi first 
::
    sudo apt-get update -y
    sudo apt-get upgrade -y

Reboot your Pi safely
::
    sudo reboot now

***************************
Raspberry Pi configurations
***************************

Enable Camera/SSH/I2C in raspi-config

Open up the configuration page and select Interfacing Options by typing this command:
::
    sudo raspi-config

Select **Serial**

Select **NO**

Keep the **Serial Port Hardware enabled**

Reboot your Pi safely
::
    sudo reboot now


**************************************************
Install the needed libraries for the PlanktonScope
**************************************************

Install CircuitPython
=====================
`Installing CircuitPython on Raspberry Pi <https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi>`_

Run the following command to install adafruit_blinka
::
    pip3 install adafruit-blinka
    sudo pip3 install adafruit-circuitpython-motorkit

Install RPi Cam Web Interface
=============================

`RPi Cam Web Interface <https://elinux.org/RPi-Cam-Web-Interface>`_

Clone the code from github and enable and run the install script with the following commands
::
    git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
    cd RPi_Cam_Web_Interface
    ./install.sh

Press Enter to allow default setting of the installation
Press Enter to start RPi Cam Web Interface now
Found what is the IP of your Raspberry Pi
::
    sudo ip addr show | grep 'inet 1'

Reach the url on a local browser : http://127.0.0.1/html/

Install Ultimate GPS HAT
========================
`Installing Adafruit GPS HAT <https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi/pi-setup>`_

`Use Python Thread with GPS HAT <http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/>`_

::
    sudo apt-get install python gpsd gpsd-clients
    
Install RGB Cooling HAT
=======================
`Installing RGB Cooling HAT <https://www.yahboom.net/study/RGB_Cooling_HAT>`_
Type these command to install:
::
    git clone https://github.com/WiringPi/WiringPi.git
    cd WiringPi
    sudo ./build
    sudo apt-get install gcc

Install Node-RED
==================
`Installing Node-RED on Raspberry Pi <https://nodered.org/docs/getting-started/raspberrypi>`_

Prerequisites
-------------
Ensure npm is able to build any binary modules it needs to install. 
::
    sudo apt-get install build-essential

Download and installation
-------------------------
To install Node.js, npm and Node-RED onto a Raspberry Pi, run the following command will that download and install them: 
::
    bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
    
Due to the limited memory of the Raspberry Pi, you will need to start Node-RED with an additional argument to tell the underlying Node.js process to free up unused memory sooner than it would otherwise.
::
    node-red-pi --max-old-space-size=256

Autostart on boot
-----------------
Run Node-RED when the Pi is turned on, or re-booted, enable the service to autostart by running the command:
::
    sudo systemctl enable nodered.service

Check the installation
----------------------
Make sure NodeRed is correctly installed by reaching the following page from the broswer of your pi :
::
    http://localhost:1880.

Install few nodes
-----------------
These nodes will be used in Node-RED:
::  
    cd .node-red/
    npm install node-red-dashboard
    npm install node-red-contrib-python3-function
    npm install node-red-contrib-camerapi
    npm install node-red-contrib-gpsd
    npm install node-red-contrib-web-worldmap

Import the last GUI
-------------------

Import the `lastest version of the GUI <https://raw.githubusercontent.com/tpollina/PlanktonScope/master/scripts/flows_planktonscope.json>`_

Install Mosquitto MQTT
======================

In order to send and receive from Node-RED:
::
    sudo apt-get install mosquitto mosquitto-clients
    

Install mqtt-paho
=================

In order to send and receive from python:
::
    pip3 install paho-mqtt
    
Install OpenCV
=================

Use the quick version without virtual env
https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/


Install MorphoCut
=================

`Installing MorphoCut <https://morphocut.readthedocs.io/en/stable/installation.html>`_

MorphoCut is packaged on PyPI and can be installed with pip:
::
    sudo apt-get install python3-scipy
    pip3 install -U git+https://github.com/morphocut/morphocut.git@pyrocystis

Finishing the install
=====================

Make sure to update your Pi 
::
    sudo apt-get update -y
    sudo apt-get full-upgrade -y

Reboot your Pi safely
::
    sudo reboot now


*******************
Usefull later maybe
*******************

Download the GitHub repo
========================
At this link : https://github.com/tpollina/PlanktonScope/archive/master.zip
Unzip to a specific location:
::
    unzip /home/pi/Downloads/PlanktonScope-master.zip -d /home/pi/
    mv /home/pi/PlanktonScope-master /home/pi/PlanktonScope

Update node-RED interface
=========================
To update the interface, you can just download the lastest .json file:
::
    wget -P $HOME/.node-red https://raw.githubusercontent.com/tpollina/PlanktonScope/master/scripts/flows_planktonscope.json
    

Share WiFi via Ethernet
=======================

At this link : https://www.instructables.com/id/Share-WiFi-With-Ethernet-Port-on-a-Raspberry-Pi/
 
