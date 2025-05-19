#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

# Determine the base path for copied files
config_files_root=$(dirname "$(realpath "$BASH_SOURCE")")

# Get command-line args
hardware_type="$1" # should be either adafruithat, planktoscopehat, fairscope-latest, or segmenter-only
default_config="$hardware_type-latest"
case "$hardware_type" in
"fairscope-latest")
  hardware_type="planktoscopehat"
  default_config="fairscope-latest"
  ;;
"segmenter-only")
  # FIXME: instead set up the segmenter-only version of the Node-RED dashboard!
  echo "Warning: setting up adafruithat version of Node-RED dashboard for hardware type: $hardware_type"
  hardware_type=adafruithat
  default_config="adafruithat-latest"
  ;;
esac

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

# Install Node.js 20
# https://github.com/nodesource/distributions/blob/master/README.md#using-debian-as-root-nodejs-20
curl -fsSL https://deb.nodesource.com/setup_20.x -o /tmp/nodesource_setup.sh
sudo -E bash /tmp/nodesource_setup.sh
sudo apt-get install -y nodejs

# Install Node-RED
npm config set prefix /home/pi/.local
npm install -g node-red@v4.0.9
sudo systemctl enable nodered.service

cp "$HOME/PlanktoScope/software/node-red-dashboard/default-configs/$default_config.config.json" \
  "$HOME"/PlanktoScope/config.json

# Configure node-red
npm --prefix "$HOME"/PlanktoScope/software/node-red-dashboard install
sudo cp $config_files_root/nodered.service /etc/systemd/system/nodered.service
sudo mkdir -p /etc/systemd/system/nodered.service.d
sudo cp $config_files_root/30-override.conf /etc/systemd/system/nodered.service.d/30-override.conf

# Install dependencies to make them available to Node-RED
npm --prefix "$HOME"/PlanktoScope/software/node-red-dashboard/$hardware_type install
