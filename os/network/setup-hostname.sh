#!/bin/bash -eu

hostname=$(cat /etc/hostname)

sudo sed -i "s/raspberrypi/$hostname/g" /etc/hosts
sudo sed -i "s/raspberrypi/$hostname/g" /etc/cockpit/cockpit.conf
sudo sed -i "s/raspberrypi/$hostname/g" /etc/NetworkManager/system-connections/wlan0-hotspot.nmconnection
