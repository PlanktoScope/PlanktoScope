#!/bin/bash -eu
# shellcheck disable=all

machine_name=""

# Allow preempting automatic machine-name generation behavior with /etc/machine-name:
if [ -f /etc/machine-name ]; then
  machine_name="$(sed 's~#.*$~~g' /etc/machine-name | tr -d '[:space:]')"
fi

if [ ! -z "$machine_name" ]; then
  echo "A machine name was manually specified in /etc/machine-name: $machine_name"
elif [ -f /sys/firmware/devicetree/base/serial-number ] && [ -x /usr/local/bin/machine-name ]; then
  # Automatically generate a machine-name from the RPi serial number if needed:
  serial_number="$(tr -d '\0' </sys/firmware/devicetree/base/serial-number | cut -c 9-)"
  machine_name="$(
    /usr/local/bin/machine-name name --format=hex --sn="$serial_number" ||
      # fall back to English in case the language setting is unrecognized:
      LANG=en_US.UTF-8 /usr/local/bin/machine-name name --format=hex --sn="$serial_number"
  )"
fi

if [ "$machine_name" = "" ] &&
  [ -f /etc/machine-id ] &&
  [ -x /usr/bin/sha256sum ] &&
  [ -x /usr/local/bin/machine-name ]; then
  serial_number="$(sha256sum /etc/machine-id | cut -c 1-8)"
  machine_name="$(
    /usr/local/bin/machine-name name --format=hex --sn="$serial_number" ||
      # fall back to English in case the language setting is unrecognized:
      LANG=en_US.UTF-8 /usr/local/bin/machine-name name --format=hex --sn="$serial_number"
  )"
fi

if [ "$machine_name" = "" ]; then
  echo "Warning: a machine name could not be generated!"
  if [ -f /run/machine-name ]; then
    echo "Using default machine name: $(cat /run/machine-name)"
  fi
  exit 1
fi

echo "Machine name: $machine_name"
printf "%s" "$machine_name" >/run/machine-name
