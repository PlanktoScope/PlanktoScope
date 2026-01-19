#!/bin/bash -eux

device=$1
name=$2
file=$name.img

# save raspios sdcard
dd bs=1M if="$device" status=progress conv=fdatasync of="$file"

# resize
# TODO resize /dev/mmcblk0p1
# TODO make /dev/mmcblk0p1 exfat label PKSCOPE

# TODO

# Add one of to /etc/fstab
# LABEL=PKSCOPE  /home/pi/data      exfat   defaults,noatime,nofail,umask=000  0  2
# /dev/mmcblk0p3  /home/pi/data      exfat   defaults,noatime,nofail,umask=000  0  2

# shrink
pishrink.sh -Za "$file"

# compress
# xz -T0 -9 -k $file
