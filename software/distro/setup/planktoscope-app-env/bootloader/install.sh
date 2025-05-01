#!/bin/bash -eux
# Update and configure the bootloader
# https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#update-the-bootloader-configuration

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
distro_setup_files_root="$(dirname "$(dirname "$config_files_root")")"
repo_root="$(dirname "$(dirname "$(dirname "$distro_setup_files_root")")")"

sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  rpi-eeprom

cp /usr/lib/firmware/raspberrypi/bootloader-2712/latest/pieeprom-2025-03-19.bin /tmp
cp /usr/lib/firmware/raspberrypi/bootloader-2712/latest/recovery.bin /tmp

rpi-eeprom-config /tmp/pieeprom-2025-03-19.bin --config "$config_files_root/boot.conf" --out /tmp/pieeprom.upd
rpi-eeprom-digest -i /tmp/pieeprom.upd -o /tmp/pieeprom.sig

# /boot and not /boot/firmware
# see https://github.com/ethanjli/pinspawn-action/issues/5
sudo cp pieeprom.bin pieeprom.sig recovery.bin /boot/

# The bootloader will be installed on first boot and the files removed
# see https://github.com/PlanktoScope/PlanktoScope/pull/589
