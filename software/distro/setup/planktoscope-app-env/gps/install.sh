#!/bin/bash -eux
# The GPS driver provides support for a GPS device over serial, as well as system clock updating
# from GPS.

# Determine the base path for copied files
config_files_root=$(dirname "$(realpath "$BASH_SOURCE")")

# Install dependencies
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  gpsd pps-tools chrony

# The following command enables the serial port but disables the login shell over the serial port.
# We use this because the serial port is reserved for a GPS device.
# Note that this overrides a setting in the base-os/platform-hardware/config.sh script.
sudo raspi-config nonint do_serial_cons 1

# Enable automatic time update from GPSD
file="/boot/firmware/config.txt"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""
