#!/bin/bash -eux

serial_number="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
machine_name="$(/home/pi/.local/bin/machine-name name --format=hex --sn="$serial_number")"

ssid="$(sed "s/{machine-name}/$machine_name/g" /home/pi/.local/etc/hostapd/ssid.snippet | sed 's/#.*$//g' | sed '^$/d')"
sed -i "s/^ssid=.*$/ssid=$ssid/g" /etc/hostapd/hostapd.conf
