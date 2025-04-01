# Tips and tricks

This section provides useful snippets and how-tos while developping software for the PlanktoScope.

!!! warning

    This document is meant for PlanktoScope developers. Proceed with care.

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