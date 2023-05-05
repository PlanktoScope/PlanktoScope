#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Install dependencies
sudo apt-get update -y
sudo apt-get install -y git python3-pip

# Get the list of Python dependencies
mkdir -p /home/pi/PlanktoScope
git clone https://github.com/PlanktoScope/PlanktoScope /home/pi/PlanktoScope

# Install Python dependencies
export PATH="/home/pi/.local/bin:$PATH"
pip3 install -y -U -r /home/pi/PlanktoScope/requirements.txt
# Install opencv-contrib-python-headless instead of opencv-contrib-python
# TODO: just update the requirements.txt file instead
pip3 uninstall -y opencv-contrib-python
pip3 install -y opencv-contrib-python-headless
# Upgrade adafruit dependencies
# TODO: just update the requirements.txt file instead
pip3 install -y -—upgrade adafruit-blinka adafruit-platformdetect

# Install Fan HAT dependencies
sudo apt install -y i2c-tools
mkdir -p /home/pi/libraries
git clone https://github.com/WiringPi/WiringPi /home/pi/libraries/WiringPi
sudo /home/pi/libraries/WiringPi/build
