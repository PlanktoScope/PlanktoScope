#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Install dependencies
sudo apt-get update -y
# FIXME: if we're not using libhdf5, libopenjp2-7, libopenexr25, libavcodec58, libavformat58, and
# libswscale5, can we avoid the need to install them? Right now they're required because the Python
# backend is doing an `import * from cv2`, which is wasteful and also pollutes the namespace - if we
# only import the required subpackages from cv2, maybe we can avoid the need to install unnecessary
# dependencies via apt-get?
sudo apt-get install -y git python3-pip libatlas3-base \
  libhdf5-103-1 libopenjp2-7 libopenexr25 libavcodec58 libavformat58 libswscale5

# Install Fan HAT dependencies
sudo apt install -y i2c-tools
mkdir -p /home/pi/libraries
# FIXME: can we get a reproducible build of WiringPi? Or maybe just Python library support via pip?
git clone https://github.com/WiringPi/WiringPi /home/pi/libraries/WiringPi
# cd into WiringPi's directory because WiringPi's build script only knows how to run from there
cd /home/pi/libraries/WiringPi
sudo /home/pi/libraries/WiringPi/build
cd /home/pi

# Install Python dependencies
export PATH="/home/pi/.local/bin:$PATH"
# Note: the following command emits warnings about installed scripts not being in the user’s PATH,
# but the installed scripts will be in the user’s path after reboot:
pip3 install -U -r /home/pi/PlanktoScope/requirements.txt
