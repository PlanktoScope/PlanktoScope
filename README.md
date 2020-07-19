# PlanktoScop Main Repository
The PlanktoScop is an open and affordable modular imaging platform for citizen oceanography.

This GitHub is part of a community that you can find on [its website](https://www.planktonscope.org/).

# Fast Setup

Before going further, notice that you can download the image disk already setup without having to deal with all these command lines.
Jump here : http://planktonscope.su.domains/Images_raspberry/Raspbian_Buster_Morphocut_WiFi.img

# Expert Setup
After getting your kit and finding the necessary components, but before assembling your kit, you should take the time to do a mockup build and setup your Raspberry.

## Install and setup Raspbian on your Raspberry Pi

### Computer setup
In order to make it easy to connect to the PlanktoScop, you may want to install [avahi](https://en.wikipedia.org/wiki/Avahi_%28software%29) or the [Bonjour](https://en.wikipedia.org/wiki/Bonjour_%28software%29) service on any computer you will use to access the PlanktoScop interface. This will allow you to connect to the PlantoScop using an address similar such as http://planktoscope.local instead of an IP address.

### Download the image

The latest Raspbian version can always be downloaded from [the Raspberry Pi Downloads page](https://www.raspberrypi.org/downloads/raspbian/).
For a first build, it's recommende to download an image of Raspbian Buster with desktop.

#### Writing an image to the SD card

Download the latest version of [balenaEtcher](https://www.balena.io/etcher/) and install it.

Connect an SD card reader with the micro SD card inside.

Open balenaEtcher and select from your hard drive the image zip file you just downloaded.

Select the SD card you want to write your image to.

Review your selections and click `Flash!` to begin writing data to the SD card.

#### Prepare your Raspberry Pi
[Getting Started with your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/)

Plug the SD Card in your Raspberry Pi and connect your Pi to a screen, mouse and a keyboard. Check the connection twice before plugging the power.

The first boot to the desktop may take up to 120 seconds. This is normal and is caused by the image expanding the filesystem to the whole SD card. DO NOT REBOOT before you reach the desktop.

#### Finish the setup

Make sure you have access to internet and update/upgrade your fresh Raspbian install.

Update your Pi first. Open up a terminal, and do the following:
```sh
sudo apt-get update -y
sudo apt-get upgrade -y
```

You can now reboot your Pi safely.
```sh
sudo reboot now
```

## Raspberry Pi configurations

### Enable Camera/SSH/I2C in raspi-config

Open up a terminal once again, and access the configuration tool:
```sh
sudo raspi-config
```

While you're here, a wise thing to do would be to change the default password for the `pi` user. This is very warmly recommended if your PlanktoScop is connected to a shared network you do not control. Just select the first option `1 Change User Password`.

Now, you can go to `5 Interfacing Options`, then `P2 SSH`. Choose `Yes` to activate the SSH access.

Again, select `5 Interfacing Options`, then `P4 SPI`. Choose `Yes` to enable the SPI interface.

One more, select `5 Interfacing Options`, then `P5 I2C`. Choose `Yes` to enable the ARM I2C interface of the Raspberry.

Finally, select `5 Interfacing Options`, then `P6 Serial`.

This time, choose `No` to deactivate the login shell on the serial connection, but then choose `Yes` to keep the Serial port hardware enabled.

These steps can also be done from the Raspberry Pi Configuration GUI tool that you can find in `Main Menu > Preferences`. Go to the `Interfaces` tab. Pay attention, here the Serial Port must be enabled, but the Serial Port Console must be disabled.

Reboot your Pi safely.
```sh
sudo reboot now
```

## Install the needed libraries for the PlanktoScop

### Install CircuitPython
Start by following [Adafruit's guide](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi). You can start at the chapter `Install Python Libraries`.

For the record, the command are as following, however, Adafruit's page might have been updated, so please make sure this is still needed:
```sh
pip3 install RPI.GPIO
pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-motorkit
```

### Install RPi Cam Web Interface

You can find more information about the RPi Cam Web Interface on [eLinux' website](https://elinux.org/RPi-Cam-Web-Interface).

To set it up, clone the code from Github and enable and run the install script with the following commands
```sh
git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
cd RPi_Cam_Web_Interface
./install.sh
```

Press Enter to allow default setting of the installation.
Press Enter to start RPi Cam Web Interface now.
Found what is the IP of your Raspberry Pi.
```
sudo ip addr show | grep 'inet 1'
```
You can test the interface locally by accessing this url in from the browser in the Raspberry: `http://localhost/html`

You can also try to access this page from another computer connected to the same network with the IP address previously found : `http://[IP_ADDRESS]/html/`. If your computer has `avahi` or the `Bonjour` service installed and running, you can also use this url: http://raspberrypi.local/html/ .


### Install Ultimate GPS HAT
[Installing Adafruit GPS HAT](https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi/pi-setup)

[Use Python Thread with GPS HAT](http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/)

```
sudo apt-get install python gpsd gpsd-clients
```

### Install RGB Cooling HAT
[Installing RGB Cooling HAT](https://www.yahboom.net/study/RGB_Cooling_HAT)

Type these command to install:
```
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
sudo ./build
sudo apt-get install gcc
```

### Install Node-RED
[Installing Node-RED on Raspberry Pi](https://nodered.org/docs/getting-started/raspberrypi)

#### Prerequisites
Ensure npm is able to build any binary modules it needs to install.
```
sudo apt-get install build-essential
```

#### Download and installation
To install Node.js, npm and Node-RED onto a Raspberry Pi, run the following command will that download and install them:
```
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
Due to the limited memory of the Raspberry Pi, you will need to start Node-RED with an additional argument to tell the underlying Node.js process to free up unused memory sooner than it would otherwise.
```
node-red-pi --max-old-space-size=256
```

#### Autostart on boot
Run Node-RED when the Pi is turned on, or re-booted, enable the service to autostart by running the command:
```sh
sudo systemctl enable nodered.service
```

#### Check the installation
Make sure NodeRed is correctly installed by reaching the following page from the broswer of your pi : http://localhost:1880.

#### Install few nodes
These nodes will be used in Node-RED:
```
cd .node-red/
npm install node-red-dashboard
npm install node-red-contrib-python3-function
npm install node-red-contrib-camerapi
npm install node-red-contrib-gpsd
npm install node-red-contrib-web-worldmap
```

#### Import the last GUI

Import the lastest version of the GUI from https://raw.githubusercontent.com/tpollina/PlanktonScope/master/scripts/flows_planktonscope.json>

### Install Mosquitto MQTT

In order to send and receive from Node-RED:
```
sudo apt-get install mosquitto mosquitto-clients

```

### Install mqtt-paho

In order to send and receive from python:
```
pip3 install paho-mqtt
```

### Install OpenCV

Use the quick version without virtual env
https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/


### Install MorphoCut
[Installing MorphoCut](https://morphocut.readthedocs.io/en/stable/installation.html)

MorphoCut is packaged on PyPI and can be installed with pip:

```sh
sudo apt-get install python3-scipy
pip3 install -U git+https://github.com/morphocut/morphocut.git
```

## Finishing the install

Make sure to update your Pi
```
sudo apt-get update -y
sudo apt-get full-upgrade -y
```

Reboot your Pi safely
```
sudo reboot now

```

## Useful later maybe

### Download the GitHub repo
At this link : https://github.com/tpollina/PlanktonScope/archive/master.zip
Unzip to a specific location:
```
unzip /home/pi/Downloads/PlanktonScope-master.zip -d /home/pi/
mv /home/pi/PlanktonScope-master /home/pi/PlanktonScope
```

### Update node-RED interface
To update the interface, you can just download the lastest .json file:
```
wget -P $HOME/.node-red https://raw.githubusercontent.com/tpollina/PlanktonScope/master/scripts/flows_planktonscope.json
```

### Share WiFi via Ethernet

At this link : https://www.instructables.com/id/Share-WiFi-With-Ethernet-Port-on-a-Raspberry-Pi/
