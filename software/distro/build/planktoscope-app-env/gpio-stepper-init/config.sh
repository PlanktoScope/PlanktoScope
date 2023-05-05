#!/bin/bash -eux
# The hardware stepper motors need to be configured for the operational behavior
# required by the PlanktoScope's overall design.

# Determine the base path for config files

config_files_root=$(dirname $(realpath $0))

# Add systemd service for initializing stepper motors
file="/etc/systemd/system/planktoscope-org.init-gpio-steppers.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.init-gpio-steppers.service

# Add shell script for initializing stepper motors
mkdir -p /home/pi/.local/bin
file="/home/pi/.local/bin/disable-gpio-steppers"
cp "$config_files_root$file" "$file"
