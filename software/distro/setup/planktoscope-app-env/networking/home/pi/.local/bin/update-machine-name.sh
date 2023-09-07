#!/bin/bash -eux

serial_number="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
machine_name="$(/home/pi/.local/bin/machine-name name --format=hex --sn="$serial_number")"

# Update /home/pi/.local/etc/machine-name
echo "$machine_name" > /home/pi/.local/etc/machine-name
