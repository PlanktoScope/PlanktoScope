#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))
distro_setup_files_root=$(dirname $(dirname $config_files_root))
repo_root=$(dirname $(dirname $(dirname $distro_setup_files_root)))

# Get command-line args
hardware_type="$1" # should be either adafruithat or planktoscopehat
if [ $hardware_type = "segmenter-only" ]; then
  echo "Warning: setting up adafruithat version of Node-RED dashboard for hardware type: $hardware_type"
  hardware_type=adafruithat
fi

# Install dependencies
# smbus is needed by some python3 nodes in the Node-RED dashboard for the Adafruit HAT.
# Since the Node-RED systemd service runs as the pi user by default (and we don't override that
# default, we do `pip3 install` as the pi user. This makes the smbus2 module available to Node-RED.
# FIXME: get rid of the Node-RED nodes depending on smbus! That functionality should be moved into
# the Python backend.
sudo apt-get install -y python3-smbus2

# Install Node-RED
# TODO: run Node-RED in a Docker container instead
curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered \
  | bash -s - --confirm-install --confirm-pi --no-init

# Select the enabled dashboard
cp "$repo_root/software/node-red-dashboard/flows/$hardware_type.json" \
  $HOME/.node-red/flows.json
cp "$repo_root/software/node-red-dashboard/default-configs/$hardware_type-latest.config.json" \
  $HOME/PlanktoScope/config.json

# Copy required dependencies with hard-coded paths in the Node-RED dashboard
# TODO: get rid of this when we remove usb_backup.sh
mkdir -p $HOME/PlanktoScope/scripts
directory="scripts/bash"
# TODO: get rid of this when we move the Node-RED dashboard out to its own repository
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
