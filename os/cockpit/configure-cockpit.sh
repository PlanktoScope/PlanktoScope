#!/bin/bash -eu

hostname=$(cat /etc/hostname)

# cockpit
sudo cp cockpit.ini /etc/cockpit/cockpit.conf
sudo sed -i "s/raspberrypi/$hostname/g" /etc/cockpit/cockpit.conf
