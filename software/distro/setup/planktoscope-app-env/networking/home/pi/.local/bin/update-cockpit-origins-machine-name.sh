#!/bin/bash -eux

serial_number="$(tr -d '\0' < /sys/firmware/devicetree/base/serial-number | cut -c 9-)"
machine_name="$(/home/pi/.local/bin/machine-name name --format=hex --sn="$serial_number")"

# Update /home/pi/.local/etc/cockpit/origins
cp /home/pi/.local/etc/cockpit/origins-autogen-warning.snippet /home/pi/.local/etc/cockpit/origins.snippet
cat /home/pi/.local/etc/cockpit/origins-base.snippet >> /home/pi/.local/etc/cockpit/origins.snippet
sed "s/\{machine-name\}/$machine_name/g" /home/pi/.local/etc/cockpit/origins-machine-name.snippet \
  >> /home/pi/.local/etc/cockpit/origins.snippet

# Update /etc/cockpit/cockpit.conf
origins="$(sed 's/#.*$//g' /home/pi/.local/etc/cockpit/origins.snippet | sed '/^$/d' | paste -s -d ' ')"
sed -i "s|^Origins = .*$|Origins = ${origins}|g" /etc/cockpit/cockpit.conf
rm /home/pi/.local/etc/cockpit/origins.snippet
