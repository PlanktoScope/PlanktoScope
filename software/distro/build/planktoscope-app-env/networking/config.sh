#!/bin/bash -eux
# The networking configuration sets PlanktoScope-specific network settings.

config_files_root=$(dirname $(realpath $0))

# Set the default hostname, which will be overwritten with the device-specific MAC-address-based ID
# on each boot
current_hostname=$(hostnamectl status --static)
new_hostname="planktoscope"
sudo bash -c "echo \"$new_hostname\" > /etc/hostname"
sudo sed -i "s/127\.0\.1\.1.*${current_hostname}/127.0.1.1\t${new_hostname}/g" /etc/hosts

# Change dnsmasq settings
file="/etc/dnsmasq.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""
mkdir -p /home/pi/.local/etc/hosts
# TODO: automatically update hostfile entries for the planktoscope based on its device name, for disambiguation
touch /home/pi/.local/etc/hosts
