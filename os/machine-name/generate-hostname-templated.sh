#!/bin/bash -eu
# shellcheck disable=all

machine_name=""

if [ -f /run/machine-name ]; then
  machine_name="$(cat /run/machine-name)"
fi
if [ -z "$machine_name" ]; then
  echo "Warning: no machine name was set at /run/machine-name! Falling back to 'unknown'."
  machine_name="unknown"
fi

if [ -f /etc/hostname-template ]; then
  hostname="$(sed 's~#.*$~~g' /etc/hostname-template | tr -d '[:space:]')"
else
  echo "Warning: no hostname template was set! Falling back to 'machine-{machine-name}."
  hostname="machine-{machine-name}"
fi

hostname="$(echo "$hostname" | sed "s~{machine-name}~${machine_name}~g")"

mkdir -p /etc
echo "Hostname: $hostname"
printf "%s" "$hostname" > /etc/hostname

sudo sed -i "s/raspberrypi/$hostname/g" /etc/hosts
sudo sed -i "s/raspberrypi/$hostname/g" /etc/cockpit/cockpit.conf
