#!/bin/bash -eux

serial_number="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
machine_name="$(/home/pi/.local/bin/machine-name name --format=hex --sn="$serial_number")"
sed -i "s/^ssid=.*$/ssid=PlanktoScope $machine_name/g" /etc/hostapd/hostapd.conf
