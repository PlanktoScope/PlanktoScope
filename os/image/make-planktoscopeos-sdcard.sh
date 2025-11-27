#!/bin/bash -eux

# save raspios sdcard
dd bs=1M if=/dev/mmcblk0 status=progress conv=fdatasync of=pkos.img

# shrink
pishrink.sh pkos.img
