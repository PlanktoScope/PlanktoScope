#!/bin/bash -eux
# The networking configuration sets PlanktoScope-specific network settings.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Set the default hostname, which will be overwritten with the device-specific MAC-address-based ID
# on each boot
current_hostname=$(hostnamectl status --static)
new_hostname="planktoscope"
sudo bash -c "echo \"$new_hostname\" > /etc/hostname"
sudo sed -i "s/127\.0\.1\.1.*${current_hostname}/127.0.1.1\t${new_hostname}/g" /etc/hosts

# Change dnsmasq settings
file="/etc/dnsmasq.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""
mkdir -p /home/pi/.local/etc
# TODO: add device-specific names which are automatically updated, for disambiguation. Something
# like "babaya-koujaini-plankto.scope" or "babaya-koujaini.planktoscope".
file="/home/pi/.local/etc/hosts"
cp "$config_files_root$file" "$file"
