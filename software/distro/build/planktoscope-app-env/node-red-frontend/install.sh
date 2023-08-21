#!/bin/bash -eux
# The Node-RED frontend provides a graphical user interface for the PlanktoScope software.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install Node-RED
# TODO: run Node-RED in a Docker container instead
curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered \
  | bash -s - --confirm-install --confirm-pi --no-init

# Create a settings file to run Node-RED in project mode
# TODO: remove the need for project mode, because it adds a requirement for the user to enter their
# name and email address the first time Node-RED is booted, and makes other manual actions required
# before the frontend becomes accessible/usable.
file="/home/pi/.node-red/settings.js"
cp "$config_files_root$file" "$file"
sudo chown 0:0 "$file"

# Create default configs for the Node-RED editor
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
# FIXME: github.com/PlanktoScope/PlanktoScope should provide a subfolder which is the Node-RED
# project to move into /home/pi/.node-red/projects, instead of having to be moved wholesale.
mkdir -p /home/pi/.node-red/projects
mv /home/pi/PlanktoScope /home/pi/.node-red/projects/PlanktoScope
ln -s /home/pi/.node-red/projects/PlanktoScope /home/pi/PlanktoScope

# Install more dependencies
# FIXME: copy-dependencies should be listed as a dev dependency somewhere in the PlanktoScope repository
# and version-locked. It would be even better if we didn't need to use copy-dependencies
npm --prefix /home/pi/.node-red install copy-dependencies
# For some reason, copy-dependencies seems to be unable to handle absolute paths in its args - instead,
# it prepends (probably) the current working directory to the args, regardless of whether they're
# absolute or relative paths. So we're forced to provide relative paths.
cd /home/pi
node /home/pi/.node-red/node_modules/copy-dependencies/index.js \
  .node-red/projects/PlanktoScope .node-red
npm --prefix /home/pi/.node-red update
