#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

## Install basic tooling
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  git python3-pip python3-venv pipx

## Install mosquitto
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  mosquitto
sudo systemctl enable mosquitto.service

# Suppress keyring dialogs when setting up the PlanktoScope distro on a graphical desktop
# (see https://github.com/pypa/pip/issues/7883)
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

# Install Poetry
pipx install poetry==2.1.3
pipx ensurepath
PATH="$PATH:/home/pi/.local/bin"

# Set up the hardware controller
sudo -E apt-get install -y --no-install-recommends -o Dpkg::Progress-Fancy=0 \
  i2c-tools libopenjp2-7 python3-picamera2
poetry --directory "$HOME/PlanktoScope/controller" install \
  --compile
file="/etc/systemd/system/planktoscope-org.controller.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable "planktoscope-org.controller.service"

# Set up the segmenter
poetry --directory "$HOME/PlanktoScope/segmenter" install \
  --compile
file="/etc/systemd/system/planktoscope-org.segmenter.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable "planktoscope-org.segmenter.service"
