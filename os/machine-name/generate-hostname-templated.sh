#!/bin/bash -eu
# shellcheck disable=all

machine_name="$(cat /run/machine-name)"
hostname="planktoscope-${machine_name}"

mkdir -p /etc
echo "Hostname: $hostname"
printf "%s" "$hostname" > /etc/hostname

sudo sed -i "s/raspberrypi/$hostname/g" /etc/hosts
sudo sed -i "s/raspberrypi/$hostname/g" /etc/cockpit/cockpit.conf
sudo sed -i "s/raspberrypi/$hostname/g" /etc/NetworkManager/system-connections/wlan0-hotspot.nmconnection
