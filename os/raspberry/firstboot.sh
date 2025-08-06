#!/bin/bash -eux

rm -f /boot/firmware/pieeprom.sig
rm -f /boot/firmware/pieeprom.upd
rm -f /boot/firmware/RECOVERY.000
rm -f /boot/firmware/recovery.bin
nmcli radio wifi on || true # See also network/justfile
