#!/bin/bash -eu
# shellcheck disable=all

# Automatically generate a machine-name from the RPi serial number
serial_number="$(tr -d '\0' </sys/firmware/devicetree/base/serial-number | cut -c 9-)"
machine_name="$(LANG=en_US.UTF-8 /usr/local/bin/machine-name name --format=hex --sn="$serial_number")"
machine_name="$(echo $machine_name | sed 's/-[0-9]*$//')"

echo "Machine name: $machine_name"
printf "%s" "$machine_name" >/run/machine-name
