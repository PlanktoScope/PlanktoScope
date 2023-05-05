#!/bin/bash -euxo pipefail
# The GPS driver provides support for a GPS device over serial, as well as system clock updating
# from GPS.

config_files_root = $(dirname $(realpath $0))

# Install dependencies
sudo apt-get update -y
sudo apt-get install -y gpsd pps-tools chrony

# Configure gpsd
file="/etc/default/gpsd"
sudo cp "$config_files_root$file" "$file"
sudo systemctl restart gpsd.service

# Enable automatic time update from GPSD
file="/boot/config.txt"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""

# Add systemd service modification to make Node-RED wait until Mosquitto has started
file="/etc/chrony/conf.d/pps-gpio.conf"
sudo cp "$config_files_root$file" "$file"
sudo systemctl stop systemd-timesyncd.service
sudo systemctl disable systemd-timesyncd.service
