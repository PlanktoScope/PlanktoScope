#!/bin/bash -eux

serial_number="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
machine_name="$(/home/pi/.local/bin/machine-name name --format=hex --sn="$serial_number")"

# Update /home/pi/.local/etc/hosts
cp /home/pi/.local/etc/hosts-autogen-warning.snippet \
  /home/pi/.local/etc/hosts
cat /home/pi/.local/etc/hosts-base.snippet \
  >> /home/pi/.local/etc/hosts
sed "s/{machine-name}/$machine_name/g" /home/pi/.local/etc/hosts-machine-name.snippet \
  >> /home/pi/.local/etc/hosts
