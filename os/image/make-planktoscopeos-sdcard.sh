#!/bin/bash -eux

# save raspios sdcard
dd bs=1M if=/dev/mmcblk0 status=progress conv=fdatasync of=pkos.img

# shrink
pishrink.sh -Za pkos.img

# compress
xz -T0 -9 -k pkos.img

# upload pkos.img.xz
