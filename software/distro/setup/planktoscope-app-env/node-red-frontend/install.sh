#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

# Determine the base path for copied files
config_files_root=$(dirname "$(realpath "$BASH_SOURCE")")
distro_setup_files_root=$(dirname "$(dirname "$config_files_root")")

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

# Prepare tool to generate machine names based on serial numbers
# Note: the tool itself is deployed/managed by Forklift.
# TODO: remove this by updating the Node-RED frontend and Python backend:
# Add a symlink at /var/lib/planktoscope/machine-name for backwards-compatibility with the Node-RED
# frontend and Python backend, which are not yet updated to check /run/machine-name instead:
sudo mkdir -p /var/lib/planktoscope
sudo rm -f /var/lib/planktoscope/machine-name
sudo ln -s /run/machine-name /var/lib/planktoscope/machine-name

# Install dependencies
# smbus is needed by some python3 nodes in the Node-RED dashboard for the Adafruit HAT.
# Since the Node-RED systemd service runs as the pi user by default (and we don't override that
# default, we do `pip3 install` as the pi user. This makes the smbus2 module available to Node-RED.
# FIXME: get rid of the Node-RED nodes depending on smbus! That functionality should be moved into
# the Python backend.
# Note: for bookworm we need to install the apt package; for bullseye there is no apt package
if ! sudo apt-get install -y python3-smbus2; then
  sudo apt-get install -y python3-pip
  pip3 install smbus2==0.4.3
fi

# Install Node-RED
# TODO: run Node-RED in a Docker container instead
curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered |
  bash -s - --confirm-install --confirm-pi --no-init

mkdir -p "$HOME"/PlanktoScope
cp "$HOME/PlanktoScope/software/node-red-dashboard/default-configs/$default_config.config.json" \
  "$HOME"/PlanktoScope/config.json

# Install dependencies in a way that makes them available to Node-RED
cp "$HOME"/PlanktoScope/software/node-red-dashboard/package.json "$HOME"/.node-red/
cp "$HOME"/PlanktoScope/software/node-red-dashboard/package-lock.json "$HOME"/.node-red/
npm --prefix "$HOME"/PlanktoScope/software/node-red-dashboard/$default_config update
