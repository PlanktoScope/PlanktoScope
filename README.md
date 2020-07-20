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
sudo apt-get install git
```

You can now reboot your Pi safely.
```sh
sudo reboot now
```

## Raspberry Pi configuration

### Clone this repository!

First of all, and to ensure you have the latest documentation available locally, you should clone this repository using git.

Simply run the following in a terminal:
```sh
git clone https://github.com/PlanktonPlanet/PlanktonScope/
```

### Enable Camera/SSH/I2C in raspi-config

You can now launch the configuration tool:
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

You can then run the following to make sure your Raspberry has the necessary components to install and build everything it needs and to create the necessary folders:

```sh
sudo apt-get install build-essential python3 python3-pip
mkdir test libraries
```

### Install CircuitPython
Start by following [Adafruit's guide](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi). You can start at the chapter `Install Python Libraries`.

For the record, the command are as following, however, Adafruit's page might have been updated, so please make sure this is still needed:
```sh
pip3 install RPI.GPIO
pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-motorkit
```

It is recommended to test this setup by creating this small script under the name `test/blinkatest.py` and running it (you can use the editor nano if you are using the terminal).
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
chmod +x test/blinkatest.py
./test/blinkatest.py
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
cd ~/libraries
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
cd ~/libraries
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
sudo ./build
gpio -v
```

The last command should output something similar to the following:
```
gpio version: 2.60
Copyright (c) 2012-2018 Gordon Henderson
This is free software with ABSOLUTELY NO WARRANTY.
For details type: gpio -warranty

Raspberry Pi Details:
  Type: Pi 4B, Revision: 01, Memory: 4096MB, Maker: Sony
  * Device tree is enabled.
  *--> Raspberry Pi 4 Model B Rev 1.1
  * This Raspberry Pi supports user-level GPIO access.

```

More information can be found on Yahboom website, on the page [Installing RGB Cooling HAT](https://www.yahboom.net/study/RGB_Cooling_HAT).


### Install Node-RED

#### Download and installation
To install Node.js, npm and Node-RED onto a Raspberry Pi, you just need to run the following command. You can review the content of this script [here](https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered).
```sh
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
Type `y` at both prompts to accept the installation and its settings.

#### Enable start on boot and launch Node-RED
To run Node-RED when the Pi is turned on or restarted, you need to enable the systemd service by running this command:
```sh
sudo systemctl enable nodered.service
```

You can now start Node-RED by running the following:
```sh
sudo systemctl start nodered.service
```

#### Check the installation
Make sure Node-RED is correctly installed by reaching the following page from the browser of your pi http://localhost:1880 or http://planktoscope.local:1880 from another computer on the same network.

#### Install the necessary nodes
These nodes will be used by the PlanktoScop software and needs to be installed:
```sh
cd ~/.node-red/
npm install node-red-dashboard node-red-contrib-python3-function node-red-contrib-camerapi node-red-contrib-gpsd node-red-contrib-web-worldmap node-red-contrib-interval
sudo systemctl restart nodered.service
```

#### Import the last GUI

From Node-RED gui in your browser, choose the Hamburger menu top right, and then Import. You can paste the code directly from the lastest version of the GUI available [here](https://raw.githubusercontent.com/PlanktonPlanet/PlanktonScope/blob/master/flows/main.json).

You can also download it directly:
```sh
wget -N -O ~/.node-red/flows_planktoscope.json https://raw.githubusercontent.com/PlanktonPlanet/PlanktonScope/master/flows/main.json
sudo systemctl restart nodered.service
```

#### More information
[Installing Node-RED on Raspberry Pi](https://nodered.org/docs/getting-started/raspberrypi)


### Install Mosquitto MQTT

In order to send and receive data from Node-RED, you need to install this. Run the following:
```
sudo apt-get install mosquitto mosquitto-clients

```

### Install mqtt-paho

In order to send and receive data from python, you need this library. Run the following:
```
pip3 install paho-mqtt
```


### Install OpenCV

We need to install the latest OpenCV version. Unfortunately, it is not available in the repositories. We are going to install it directly by using pip.

First, we need to install the needed dependencies, then we will directly install opencv:
```sh
sudo apt install libgtk-3-0 libavformat58 libtiff5 libcairo2 libqt4-test libpango-1.0-0 libopenexr23 libavcodec58 libilmbase23 libatk1.0-0 libpangocairo-1.0-0 libwebp6 libqtgui4 libavutil56 libjasper1 libqtcore4 libcairo-gobject2 libswscale5 libgdk-pixbuf2.0-0 libhdf5-dev libilmbase-dev libopenexr-dev libgstreamer1.0-dev libavcodec-dev libavformat-dev libswscale-dev libwebp-dev libatlas-base-dev
sudo pip3 install opencv-contrib-python==4.1.0.25
```

You can now check that opencv is properly installed by running a python interpreter and importing the cv2 module.
```sh
pi@planktoscope:~ $ python3
Python 3.7.3 (default, Dec 20 2019, 18:57:59)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'4.1.0'
>>> quit()
```

If all goes well, the displayed version number should be `4.1.0`.

More detailed information can be found on this [website](https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/).


### Install MorphoCut

MorphoCut is packaged on PyPI and can be installed with pip:

```sh
sudo apt-get install python3-scipy
pip3 install -U git+https://github.com/morphocut/morphocut.git
```

To test the installation, open up once again a python interpreter and import the morphocut module:
```sh
pi@planktoscope:~ $ python3
Python 3.7.3 (default, Dec 20 2019, 18:57:59)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import morphocut
>>> morphocut.__version__
'0.1.1+42.g01a051e'
>>> quit()
```

The MorphoCut documentation can be found [on this page](https://morphocut.readthedocs.io/en/stable/index.html).


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

### Update the cloned repository

Updates are published on Github regurlarly. Make sure to update once in a while by running this command:
```sh
cd PlanktonScope
git pull
```

This will pull and merge all the changes made since your last update.

### Update node-RED interface
To update the interface and make sure you run the latest version, you need to copy the json config file from the cloned repository to the Node-RED library:
```sh
cp ~/PlanktonScope/flows/main.json ~/.node-red/flows_planktoscope.json
```

### Share WiFi via Ethernet

At this link : https://www.instructables.com/id/Share-WiFi-With-Ethernet-Port-on-a-Raspberry-Pi/
