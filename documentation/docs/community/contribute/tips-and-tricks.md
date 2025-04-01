# Tips and tricks

This page provides useful snippets and how-tos while developping software for the PlanktoScope.

!!! warning

    This document is meant for PlanktoScope developers. Proceed with care.

## Development Environment

On the Raspberry, we recommend using our developer image which is built upon [Raspberry Pi OS with desktop 64-bit](https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-64-bit).

You can find the latest build in [actions](https://github.com/PlanktoScope/PlanktoScope/actions/workflows/build-os-bookworm-dx.yml?query=branch%3Amaster)

1. Choose the branch (e.g. `master`)
1. Navigate to the first action in the table
2. Download one of the Artifact depending on your PlanktoScope hardware
3. Run `unzip filename.zip` to extract files

See [Backup and Restore SD Card image](#backup-and-restore-sd-card) below to write the `.img.xz` file to the sdcard

## Backup and Restore SD Card

You will need to plug the SD card into your computer.

`/dev/device` refers to the path of the SD card device/disk. You will need to adjust it. Use `diskutil list` on macOS and `fdisk --list` on Linux.


```sh
# backup whole SD card onto an image file on your computer
sudo dd bs=1M if=/dev/device status=progress | xz > sdcard.img.xz
```

```sh
# restore an image file from your computer onto the SD card
xzcat sdcard.img.xz | sudo dd bs=1M of=/dev/mmcblk0 status=progress
```

See also the operating guide [SD Card Cloning](/operation/clone-sd/).