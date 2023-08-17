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
python3 -m pip install --user pipx==1.2.0
python3 -m pipx ensurepath
pipx install poetry==1.5.1

# Install Fan HAT dependencies
# FIXME: do we even need to do this build?
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
# TODO: pin this at a specific version (at least until we distribute it as a Docker image)
wget https://github.com/PlanktoScope/device-backend/archive/refs/heads/main.zip
unzip main.zip
rm main.zip
mv device-backend-main /home/pi/device-backend
cd /home/pi/device-backend
poetry init
cd -
