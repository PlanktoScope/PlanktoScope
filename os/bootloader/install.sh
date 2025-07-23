#!/bin/bash -eux
# Update and configure the bootloader
# https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#update-the-bootloader-configuration
# Please note that we disable self update on anything but Raspberry Pi 5; see config.txt.snippet

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  rpi-eeprom

cp /usr/lib/firmware/raspberrypi/bootloader-2712/latest/pieeprom-2025-07-17.bin /tmp
cp /usr/lib/firmware/raspberrypi/bootloader-2712/latest/recovery.bin /tmp

rpi-eeprom-config /tmp/pieeprom-2025-07-17.bin --config "$config_files_root/boot.conf" --out /tmp/pieeprom.upd
rpi-eeprom-digest -i /tmp/pieeprom.upd -o /tmp/pieeprom.sig

sudo cp /tmp/pieeprom.upd /tmp/pieeprom.sig /tmp/recovery.bin /boot/firmware/

# The bootloader will be installed on first boot and the files removed
# see https://github.com/PlanktoScope/PlanktoScope/pull/589

# https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#automaticupdates
sudo systemctl mask rpi-eeprom-update

# "The temporary EEPROM update files are automatically deleted by the rpi-eeprom-update service at startup."
# from https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#bootloader-update-files
# But we mask it to avoid auto updates so we have a custom unit file instead
sudo cp "$config_files_root"/planktoscope-org.firstboot.service /etc/systemd/system/
sudo systemctl enable planktoscope-org.firstboot.service
