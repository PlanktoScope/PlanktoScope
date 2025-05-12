#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

# Determine the base path for copied files
config_files_root=$(dirname "$(realpath "$BASH_SOURCE")")

# Get command-line args
hardware_type="$1" # should be either adafruithat, planktoscopehat, or fairscope-latest
default_config="$hardware_type-latest"
if [ "$hardware_type" = "fairscope-latest" ]; then
  hardware_type="planktoscopehat"
  default_config="fairscope-latest"
fi

# Install dependencies
# smbus is needed by some python3 nodes in the Node-RED dashboard for the Adafruit HAT.
# Since the Node-RED systemd service runs as the pi user by default (and we don't override that
# default, we do `pip3 install` as the pi user. This makes the smbus2 module available to Node-RED.
# FIXME: get rid of the Node-RED nodes depending on smbus! That functionality should be moved into
# the Python backend.
if ! sudo apt-get install -y python3-smbus2; then
  sudo apt-get install -y python3-pip
  pip3 install smbus2==0.4.3
fi

# Install Node-RED
# TODO: run Node-RED in a Docker container instead
curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered |
  bash -s - --confirm-install --confirm-pi --no-init

cp "$HOME/PlanktoScope/software/node-red-dashboard/default-configs/$default_config.config.json" \
  "$HOME"/PlanktoScope/config.json

# Configure node-red
npm --prefix "$HOME"/PlanktoScope/software/node-red-dashboard install
sudo mkdir -p /etc/systemd/system/nodered.service.d
sudo cp $config_files_root/30-override.conf /etc/systemd/system/nodered.service.d/30-override.conf

# Install dependencies to make them available to Node-RED
npm --prefix "$HOME/PlanktoScope/software/node-red-dashboard/adafruithat" install
npm --prefix "$HOME/PlanktoScope/software/node-red-dashboard/planktoscopehat" install
