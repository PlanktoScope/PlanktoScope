#!/bin/bash -eu

hostname=$(cat /etc/hostname)

# /etc/hosts
sudo cp hosts /etc/
sudo sed -i "s/raspberrypi/$hostname/g" /etc/hosts

# wifi hotspot
sudo cp wlan0-hotspot.ini /etc/NetworkManager/system-connections/wlan0-hotspot.nmconnection
# "failed to load connection: File permissions (100644) are insecure"
sudo chmod 0600 /etc/NetworkManager/system-connections/wlan0-hotspot.nmconnection
sudo sed -i "s/raspberrypi/$hostname/g" /etc/NetworkManager/system-connections/wlan0-hotspot.nmconnection

# cockpit
sudo cp ../cockpit/cockpit.ini /etc/cockpit/cockpit.conf
sudo sed -i "s/raspberrypi/$hostname/g" /etc/cockpit/cockpit.conf
