#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))
distro_setup_files_root=$(dirname $(dirname $config_files_root))
repo_root=$(dirname $(dirname $(dirname $distro_setup_files_root)))

# Get command-line args
hardware_type="$1" # should be either adafruithat or planktoscopehat

# Install dependencies
# smbus is needed by some python3 nodes in the Node-RED dashboard for the Adafruit HAT.
# Since the Node-RED systemd service runs as the pi user by default (and we don't override that
# default, we do `pip3 install` as the pi user. This makes the smbus2 module available to Node-RED.
# FIXME: get rid of the Node-RED nodes depending on smbus! That functionality should be moved into
# the Python backend.
pip3 install smbus2==0.4.3

# Install Node-RED
# TODO: run Node-RED in a Docker container instead
curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered \
  | bash -s - --confirm-install --confirm-pi --no-init

# Add systemd service modification to make Node-RED wait until Mosquitto has started
# FIXME: The Node-RED frontend should instead be fixed so that it does not need to wait until
# Mosquitto has started in order to work - until Mosquitto is up, the frontend should display a
# message to the user and ask them to wait.
sudo mkdir -p /etc/systemd/system/nodered.service.d
file="/etc/systemd/system/nodered.service.d/override.conf"
sudo cp "$config_files_root$file" "$file"
sudo systemctl daemon-reload
sudo systemctl enable nodered.service

# Select the enabled dashboard
cp "$repo_root/software/node-red-dashboard/flows/$hardware_type.json" \
  $HOME/.node-red/flows.json
cp "$repo_root/software/node-red-dashboard/default-configs/$hardware_type-latest.config.json" \
  $HOME/PlanktoScope/config.json

# Copy required dependencies with hard-coded paths in the Node-RED dashboard
# TODO: get rid of this when we move the Node-RED dashboard out to its own repository
mkdir -p $HOME/PlanktoScope/scripts
directory="scripts/bash"
cp -r "$repo_root/$directory" $HOME/PlanktoScope/$directory
mkdir -p $HOME/PlanktoScope/software/node-red-dashboard
directory="software/node-red-dashboard/default-configs"
cp -r "$repo_root/$directory" $HOME/PlanktoScope/$directory
directory="software/node-red-dashboard/flows"
cp -r "$repo_root/$directory" $HOME/PlanktoScope/$directory

# Install dependencies in a way that makes them available to Node-RED
cp $repo_root/software/node-red-dashboard/package.json $HOME/.node-red/
cp $repo_root/software/node-red-dashboard/package-lock.json $HOME/.node-red/
npm --prefix $HOME/.node-red update
