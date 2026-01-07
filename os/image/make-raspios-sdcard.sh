#!/bin/bash -eux

file=2025-11-24-raspios-trixie-arm64-lite.img.xz
url=https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-11-24/$file
device=/dev/mmcblk0
sha256="1d448a6e665e1ae8100bc28b35408619ec626a2fddfd6579ec99e7996fa09a56"

# download raspios
wget -c -nc "${url}"

# download signature
wget -c -nc "${url}.sha256"

# make sure signature hasn't changed
head -c 64 ${file}.sha256 | grep -qx "${sha256}"

# verify signature
cat ${file}.sha256 | sha256sum --check

# unmount
umount -q ${device}? || true
umount -q ${device} || true

# new empty dos partition table
echo 'label: dos' | sfdisk $device

# write raspios
xzcat $file | dd bs=1M of=$device status=progress conv=fdatasync

# mount boot partition
mount ${device}p1 /mnt

# create user
echo "pi:$(echo 'copepode' | openssl passwd -6 -stdin)" > /mnt/userconf

# enable ssh
touch /mnt/ssh

# unmount boot partition
umount /dev/mmcblk0p1

echo "✅ SD card is ready."
