#!/bin/bash -eux

SERIAL_NUMBER="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
MACHINE_NAME="$(/home/pi/.local/bin/machine-name name --format=hex --sn="$SERIAL_NUMBER")"
cp /home/pi/.local/etc/hosts-base.snippet /home/pi/.local/etc/hosts
sed "s/machine-name/$MACHINE_NAME/g" /home/pi/.local/etc/hosts-machine-name.snippet \
  >> /home/pi/.local/etc/hosts
