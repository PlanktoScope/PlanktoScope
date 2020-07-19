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

## Raspberry Pi configuration

### Enable Camera/SSH/I2C in raspi-config

Open up a terminal once again, and access the configuration tool:
```sh
sudo raspi-config
```

While you're here, a wise thing to do would be to change the default password for the `pi` user. This is very warmly recommended if your PlanktoScop is connected to a shared network you do not control. Just select the first option `1 Change User Password`.

You may also want to change the default hostname of your Raspberry. To do so, choose option `2 Network Options` then `N1 Hostname`. Choose a new hostname. We recommend using `planktoscope`.

We need to activate a few things for the PlanktoScop to work properly.

First, we need to activate the camera interface. Choose `5 Interfacing Options`, then `P1 Camera` and `Yes`.

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

Most of the following happens in a command line environment. If you are using the desktop, please start a terminal emulator.

You can also connect to your PlanktoScop by using ssh using `ssh pi@planktoscope.local`.

You can then run the following to make sure your Raspberry has the necessary components to install and build everything it needs:

```sh
sudo apt-get install build-essential python3 python3-pip git
```

### Install CircuitPython
Start by following [Adafruit's guide](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi). You can start at the chapter `Install Python Libraries`.

For the record, the command are as following, however, Adafruit's page might have been updated, so please make sure this is still needed:
```sh
pip3 install RPI.GPIO
pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-motorkit
```

It is recommended to test this setup by creating this small script under the name `blinkatest.py` and running it:
```python
#!/usr/bin/python3
import board
import digitalio
import busio


print("Hello blinka!")

# Try to great a Digital input
pin = digitalio.DigitalInOut(board.D4)
print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

print("done!")
```

To run the script, just run the following:
```sh
chmod +x blinkatest.py
./blinkatest.py
```

The output should be similar to this:
```
pi@planktoscope:~ $ ./test/blinkatest.py
Hello blinka!
Digital IO ok!
I2C ok!
SPI ok!
done!
```

### Install RPi Cam Web Interface

You can find more information about the RPi Cam Web Interface on [eLinux' website](https://elinux.org/RPi-Cam-Web-Interface).

To set it up, clone the code from Github and enable and run the install script with the following commands
```sh
git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
cd RPi_Cam_Web_Interface
./install.sh
```

Press Enter to allow default setting of the installation. Once everything is installed, press Enter to start the RPi Cam Web Interface now.

To test the interface locally, try accessing this url from the browser in the Raspberry: http://localhost/html

You can also try to access this page from another computer connected to the same network.

If your computer has `avahi` or the `Bonjour` service installed and running, you can directly use this url: http://raspberrypi.local/html/ .

If this is not the case, you first need to find the IP address of your Raspberry Pi by running the following:
```sh
sudo ip addr show | grep 'inet 1'
```

The web page can then be accessed at `http://[IP_ADDRESS]/html/`.

If the interface is loading and a picture is displayed, you can stop this interface for now by simply running `./stop.sh`.


### Install Ultimate GPS HAT

You can start by testing that the GPS module is working. Either install your PlanktoScop with a view of the sky, or connect the external antenna.

Now you need to run the following:
```sh
sudo apt-get install gpsd gpsd-clients
stty -F /dev/serial0 raw 9600 cs8 clocal -cstopb
cat /dev/serial0
```

If the GPS works, you should now see NMEA sentences scrolling:
```
$GPGGA,000908.799,,,,,0,00,,,M,,M,,*7E
$GPGSA,A,1,,,,,,,,,,,,,,,*1E
$GPGSV,1,1,00*79
$GPRMC,000908.799,V,,,,,0.00,0.00,060180,,,N*44
$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32
$GPGGA,000909.799,,,,,0,00,,,M,,M,,*7F
$GPGSA,A,1,,,,,,,,,,,,,,,*1E
$GPRMC,000909.799,V,,,,,0.00,0.00,060180,,,N*45
$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32
$GPGGA,000910.799,,,,,0,00,,,M,,M,,*77
$GPGSA,A,1,,,,,,,,,,,,,,,*1E
$GPRMC,000910.799,V,,,,,0.00,0.00,060180,,,N*4D
$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32
```

Until you get a GPS fix, most of the sentences are empty (see the lines starting with GPGSA and with lot of commas).


You can find more information in this hardware module in Adafruit documentation at [Installing Adafruit GPS HAT](https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi/overview) or on this page to [use Python Thread with GPS HAT](http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/)


### Install RGB Cooling HAT
To setup the RGB Cooling HAT, you just need to clone and build the WiringPi library:
```sh
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
sudo ./build
gpio -v
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
