#!/bin/bash -eux

rfkill unblock wifi || true
nmcli radio wifi on || true
nmcli connection up wlan0-hotspot

rm -f /boot/firmware/pieeprom.sig
rm -f /boot/firmware/pieeprom.upd
rm -f /boot/firmware/RECOVERY.000
rm -f /boot/firmware/recovery.bin
