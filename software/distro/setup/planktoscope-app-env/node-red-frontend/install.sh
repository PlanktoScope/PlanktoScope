#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Get command-line args
hardware_type="$1" # should be either adafruithat or pscopehat

# Install Node-RED
# TODO: run Node-RED in a Docker container instead
curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered \
  | bash -s - --confirm-install --confirm-pi --no-init

# Create a settings file to run Node-RED in project mode
file="/home/pi/.node-red/settings.js"
cp "$config_files_root$file" "$file"
sudo chown 0:0 "$file"

# Create default configs for the Node-RED editor, so that the no manual actions (e.g. entry of name
# and email address) are required the first time Node-RED is started in order for the frontend to
# become usable.
# FIXME: don't use project mode for Node-RED.
file="/home/pi/.node-red/.config.projects.json"
cp "$config_files_root$file" "$file"
file="/home/pi/.node-red/.config.users.json"
cp "$config_files_root$file" "$file"

# Add systemd service modification to make Node-RED wait until Mosquitto has started
# FIXME: The Node-RED frontend should instead be fixed so that it does not need to wait until
# Mosquitto has started in order to work - until Mosquitto is up, the frontend should display a
# message to the user and ask them to wait.
sudo mkdir -p /etc/systemd/system/nodered.service.d
file="/etc/systemd/system/nodered.service.d/override.conf"
sudo cp "$config_files_root$file" "$file"
sudo systemctl daemon-reload
sudo systemctl enable nodered.service

# Move the PlanktoScope project into a Node-RED project
mkdir -p /home/pi/.node-red/projects
mv /home/pi/PlanktoScope/software/node-red-dashboard /home/pi/.node-red/projects/PlanktoScope
ln -s /home/pi/.node-red/projects/PlanktoScope /home/pi/PlanktoScope/software/node-red-dashboard

# Select the enabled dashboard
cp -r "/home/pi/.node-red/projects/PlanktoScope/flows-$hardware_type" /home/pi/.node-red/projects/PlanktoScope/flows

# Install dependencies in a way that makes them available to Node-RED
cp /home/pi/.node-red/projects/PlanktoScope/package.json /home/pi/.node-red/
cp /home/pi/.node-red/projects/PlanktoScope/package-lock.json /home/pi/.node-red/
npm --prefix /home/pi/.node-red update
