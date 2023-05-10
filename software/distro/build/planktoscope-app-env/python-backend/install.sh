#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Install dependencies
sudo apt-get update -y
# FIXME: if we're not using libhdf5, libopenjp2-7, libopenexr25, libavcodec58, libavformat58,
# libswscale5 libgtk-3-0
# can we avoid the need to install them? Right now they're required because the Python backend is
# doing an `import * from cv2`, which is wasteful and also pollutes the namespace - if we only
# import the required subpackages from cv2, and if we could use opencv-contrib-python-headless,
# maybe we can avoid the need to install unnecessary dependencies via apt-get?
sudo apt-get install -y git python3-pip libatlas3-base \
  libhdf5-dev libopenjp2-7-dev libopenexr25 libavcodec58 libavformat58 libswscale5 libgtk-3-0

# Install Fan HAT dependencies
sudo apt install -y i2c-tools
mkdir -p /home/pi/libraries
# FIXME: can we get a reproducible build of WiringPi? Or maybe just Python library support via pip?
git clone https://github.com/WiringPi/WiringPi /home/pi/libraries/WiringPi
# cd into WiringPi's directory because WiringPi's build script only knows how to run from there
cd /home/pi/libraries/WiringPi
sudo /home/pi/libraries/WiringPi/build
cd /home/pi

# Get the list of Python dependencies
mkdir -p /home/pi/PlanktoScope
# FIXME: just instead use the repo which was downloaded to provide this shell script instead (will
# require renaming the repo directory before running the top-level build script)
git clone https://github.com/PlanktoScope/PlanktoScope /home/pi/PlanktoScope

# Remove conflicting Python dependencies from the system
sudo apt-get remove -y python3-numpy
sudo apt-get autoremove

# Install Python dependencies
export PATH="/home/pi/.local/bin:$PATH"
# FIXME: the following command is a workaround for the lack of proper version locking of pandas as
# an indirect dependency, and probably only needed for a few days until pip can find the pandas 2.0.1
# binary on piwheels
pip3 install pandas --prefer-binary
# Note: the following command emits warnings about installed scripts not being in the user’s PATH,
# but the installed scripts will be in the user’s path after reboot:
pip3 install -U -r /home/pi/PlanktoScope/requirements.txt
# Upgrade adafruit dependencies
# TODO: just update the requirements.txt file instead
pip3 install --upgrade adafruit-blinka adafruit-platformdetect
