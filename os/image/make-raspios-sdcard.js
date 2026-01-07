#!/bin/env node

import { $ } from "execa"

process.env.NODE_DEBUG = "execa"

const file = "2025-11-24-raspios-trixie-arm64-lite.img.xz"
const url = `https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-11-24/${file}`
const device = "/dev/mmcblk0"
const sha256 =
  "1d448a6e665e1ae8100bc28b35408619ec626a2fddfd6579ec99e7996fa09a56"

// download raspios
await $`wget -c -nc ${url}`

// download signature
await $`wget -c -nc ${url}.sha256`

// make sure signature hasn't changed
await $`head -c 64 ${file}.sha256`.pipe`grep -qx ${sha256}`

// verify signature
await $`cat ${file}.sha256`.pipe`sha256sum --check`

// unmount
await $({ reject: false })`umount -q ${device}?`
await $({ reject: false })`umount -q ${device}`

// create new dos partition table
await $`echo 'label: dos' | sfdisk ${device}`

// write raspios
await $`xzcat ${file}`
  .pipe`dd bs=1M of=${device} status=progress conv=fdatasync`

// mount boot partition
await $`mount ${device}p1 /mnt`

// create user
await $`echo "pi:$(echo 'copepode' | openssl passwd -6 -stdin)" > /mnt/userconf`

// enable ssh
await $`touch /mnt/ssh`

// unmount boot partition
await $`umount /dev/${device}p1`

console.log("✅ SD card is ready.")
