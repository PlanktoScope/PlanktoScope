#!/bin/bash -eux

serial_number="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
machine_name="$(/home/pi/.local/bin/machine-name name --format=hex --sn="$serial_number")"

# Update /etc/hosts and the active system hostname
current_hostname=$(hostnamectl status --static)
new_hostname="pkscope-$machine_name"
sed -i "s/^127\.0\.1\.1.*$/127.0.1.1\t${new_hostname}/g" /etc/hosts
hostnamectl set-hostname "pkscope-$machine_name"
