#!/bin/bash -eux
# The GPS driver provides support for a GPS device over serial, as well as system clock updating
# from GPS.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install dependencies
sudo apt-get update -y
sudo apt-get install -y gpsd pps-tools chrony

# The following command enables the serial port but disables the login shell over the serial port.
# We use this because the serial port is reserved for a GPS device.
# Note that this overrides a setting in the base-os/platform-hardware/config.sh script.
DISTRO_VERSION_ID="$(. /etc/os-release && echo "$VERSION_ID")"
if [ $DISTRO_VERSION_ID -ge 12 ]; then # Support Raspberry Pi OS 12 (bookworm)
  sudo raspi-config nonint do_serial_cons 1
else # Support Raspberry Pi OS 11 (bullseye)
  sudo raspi-config nonint do_serial 2
fi

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
