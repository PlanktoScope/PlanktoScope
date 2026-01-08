#!/bin/bash -eux

date=$(cat ../raspios_date)

file=${date}-raspios-trixie-arm64-lite.img.xz
url=https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-${date}/${file}
device=$1
sha256="681a775e20b53a9e4c7341d748a5a8cdc822039d8c67c1fd6ca35927abbe6290"

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

sudo partprobe $device

# find first partition
boot_partition=$(lsblk -ln -o NAME $device | sed -n '2p')

# mount boot partition
mount /dev/${boot_partition} /mnt

# create user
echo "pi:$(echo 'copepode' | openssl passwd -6 -stdin)" > /mnt/userconf

# enable ssh
touch /mnt/ssh

# unmount boot partition
umount /dev/${boot_partition}

echo "✅ SD card is ready."
