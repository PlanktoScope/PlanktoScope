#!/bin/bash -eux

# download raspios
wget -c https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-11-24/2025-11-24-raspios-trixie-arm64-lite.img.xz

# download signature
wget -c https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-11-24/2025-11-24-raspios-trixie-arm64-lite.img.xz.sha256

# make sure signature hasn't changed
head -c 65 2025-11-24-raspios-trixie-arm64-lite.img.xz.sha256 | grep -qx "1d448a6e665e1ae8100bc28b35408619ec626a2fddfd6579ec99e7996fa09a56 "

# verify signature
cat 2025-11-24-raspios-trixie-arm64-lite.img.xz.sha256 | sha256sum --check

# unmount
umount -q /dev/mmcblk0 || true
umount -q /dev/mmcblk0p1 || true
umount -q /dev/mmcblk0p2 || true

# new empty dos partition table
echo 'label: dos' | sfdisk /dev/mmcblk0

# write raspios
xzcat 2025-11-24-raspios-trixie-arm64-lite.img.xz | dd bs=1M of=/dev/mmcblk0 status=progress conv=fdatasync

# mount boot partition
mount /dev/mmcblk0p1 /mnt

# create user
echo "pi:$(echo 'copepode' | openssl passwd -6 -stdin)" > /mnt/userconf

# enable ssh
touch /mnt/ssh

# unmount boot partition
umount /dev/mmcblk0p1

echo "✅ SD card is ready."
