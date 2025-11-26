#!/bin/bash -eu

hostname=$(cat /etc/hostname)
machine_name=$(cat /run/machine-name)

sed -i "s/raspberrypi/$hostname/g" /etc/hosts || true
sed -i "s/raspberrypi/$hostname/g" /etc/cockpit/cockpit.conf || true
sed -i "s/raspberrypi/PlanktoScope $machine_name/g" /etc/NetworkManager/system-connections/wlan0-hotspot.nmconnection || true
