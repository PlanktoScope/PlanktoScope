#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install Node-RED
# TODO: run Node-RED in a Docker container instead
curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered \
  | bash -s - --confirm-install --confirm-pi

# Create a settings file to run Node-RED in project mode
# TODO: remove the need for project mode, because it adds a requirement for the user to enter their
# name and email address the first time Node-RED is booted, and makes other manual actions required
# before the frontend becomes accessible/usable.
file="/home/pi/.node-red/settings.js"
cp "$config_files_root$file" "$file"

# Add systemd service modification to make Node-RED wait until Mosquitto has started
# FIXME: The Node-RED frontend should instead be fixed so that it does not need to wait until
# Mosquitto has started in order to work - until Mosquitto is up, the frontend should display a
# message to the user and ask them to wait.
sudo mkdir -p /etc/systemd/system/nodered.service.d
file="/etc/systemd/system/nodered.service.d/override.conf"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable nodered.service

# Move the PlanktoScope project into a Node-RED project
mkdir -p /home/pi/.node-red/projects
mv /home/pi/PlanktoScope /home/pi/.node-red/projects/PlanktoScope
ln -s /home/pi/.node-red/projects/PlanktoScope /home/pi/PlanktoScope

# Install more dependencies
npm --prefix /home/pi/.node-red install copy-dependencies
node run /home/pi/.node-red/node_modules/copy-dependencies/index.js \
  /home/pi/.node-red/projects/PlanktoScope /home/pi/.node-red
npm --prefix /home/pi/.node-red update
