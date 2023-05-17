#!/bin/bash -eux

SERIAL_NUMBER="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
MACHINE_NAME="$(/home/pi/.local/bin/machine-name name —format=hex —sn="$SERIAL_NUMBER")"
sed -i "s/^ssid=.*$/ssid=PlanktoScope $MACHINE_NAME/g" /etc/hostapd/hostapd.conf
