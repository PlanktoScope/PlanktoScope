#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Get command-line args
hardware_type="$1" # should be either adafruithat or pscopehat

## Install basic Python tooling
sudo apt-get update -y
sudo apt-get install -y git python3-pip python3-venv

# Install Poetry
# Note: Because the poetry installation process (whether with pipx or the official installer) always
# selects the most recent version of the cryptography dependency, we must instead do a manual poetry
# installation to ensure that a wheel is available from piwheels for the cryptography dependency.
# We have had problems in the past with a version of that dependency not being available from
# piwheels.
POETRY_VENV=/home/pi/.local/share/pypoetry/venv
mkdir -p $POETRY_VENV
python3 -m venv $POETRY_VENV
$POETRY_VENV/bin/pip install --upgrade pip==23.3.1 setuptools==68.2.2
$POETRY_VENV/bin/pip install cryptography==41.0.5
$POETRY_VENV/bin/pip install poetry==1.6.1
# Workaround for https://github.com/python-poetry/poetry/issues/3219, from
# https://github.com/python-poetry/poetry/issues/3219#issuecomment-1540969935
$POETRY_VENV/bin/poetry config installer.parallel false

# Install pipx (not required, but useful)
python3 -m pip install --user pipx==1.2.0
python3 -m pipx ensurepath

# Download device-backend monorepo
backend_version="0c43679de9c8709f66b554c62cc6094c865a4d37" # this should be either a version tag, branch name, or commit hash
backend_version_type="hash" # this should be either "version-tag", "branch", or "hash"
case "$backend_version_type" in
  "version-tag")
    wget "https://github.com/PlanktoScope/device-backend/archive/refs/tags/$backend_version.zip"
    ;;
  "branch")
    wget "https://github.com/PlanktoScope/device-backend/archive/refs/heads/$backend_version.zip"
    ;;
  "hash")
    wget "https://github.com/PlanktoScope/device-backend/archive/$backend_version.zip"
    ;;
  *)
    echo "Unknown backend version type $backend_version_type"
    exit 1
    ;;
esac
unzip "$backend_version.zip"
rm "$backend_version.zip"
case "$backend_version_type" in
  "version-tag")
    mv "device-backend-${backend_version#"v"}" /home/pi/device-backend
    ;;
  "branch")
    mv "device-backend-$(sed 's/\//-/g' <<< $backend_version)" /home/pi/device-backend
    ;;
  "hash")
    mv "device-backend-$backend_version" /home/pi/device-backend
    ;;
  *)
    echo "Unknown backend version type $backend_version_type"
    exit 1
    ;;
esac

# Set up the hardware controllers
sudo apt-get install -y i2c-tools
$POETRY_VENV/bin/poetry --directory /home/pi/device-backend/control install
file="/etc/systemd/system/planktoscope-org.device-backend.controller-adafruithat.service"
sudo cp "$config_files_root$file" "$file"
# or for the PlanktoScope HAT
file="/etc/systemd/system/planktoscope-org.device-backend.controller-pscopehat.service"
sudo cp "$config_files_root$file" "$file"
# FIXME: make this directory in the main.py file
sudo mkdir -p /home/pi/PlanktoScope/device-backend-logs/control

# Select the enabled hardware controller
sudo systemctl enable "planktoscope-org.device-backend.controller-$hardware_type.service"
cp "/home/pi/device-backend/default-configs/$hardware_type-latest.hardware.json" \
  /home/pi/PlanktoScope/hardware.json

# Set up the data processing segmenter
# FIXME: if we're not using libhdf5, libopenjp2-7, libopenexr25, libavcodec58, libavformat58, and
# libswscale5, can we avoid the need to install them? Right now they're required because the Python
# backend is doing an `import * from cv2`, which is wasteful and also pollutes the namespace - if we
# only import the required subpackages from cv2, maybe we can avoid the need to install unnecessary
# dependencies via apt-get?
sudo apt-get install -y libatlas3-base \
  libhdf5-103-1 libopenjp2-7 libopenexr25 libavcodec58 libavformat58 libswscale5
$POETRY_VENV/bin/poetry --directory /home/pi/device-backend/processing/segmenter install
file="/etc/systemd/system/planktoscope-org.device-backend.processing.segmenter.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.device-backend.processing.segmenter.service
# FIXME: make this directory in the main.py file
sudo mkdir -p /home/pi/PlanktoScope/device-backend-logs/processing/segmenter
