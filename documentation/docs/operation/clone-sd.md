# Clone your SD card

If you want to create an SD card image from your PlanktoScope to use on other PlanktoScopes, you can follow the following steps.

## Prepare the SD card for cloning

### Prepare for cloning to other machines

Normally, your SD card contains some information (a machine-specific ID, system secrets, and SSH secrets) which should never be replicated across multiple PlanktoScopes, and some information (apt package cache) which you would probably consider a waste of space which unnecessarily increases the size of the SD card image you want to make. We provide an experimental preparation script at `/usr/libexec/prepare-custom-image` to remove this information; it also allows an SD card image created from your SD card to automatically resize itself to match the size of any SD card it's flashed to in the future. After you make any changes you want to make on your PlanktoScope for your SD card image, you should run the preparation script on the PlanktoScope with the command:

```
sudo /usr/libexec/prepare-custom-image
```

Once this script finishes running, it will shut down your PlanktoScope's Raspberry Pi. Next, you should remove the SD card from your PlanktoScope and plug it into another computer, so that you can clone the SD card into an SD card image; this guide assumes that your other computer runs Linux.

With your SD card plugged into your computer, you can mount its `rootfs` partition to delete any other sensitive files which were not removed by the `/usr/libexec/prepare-custom-image` script. For example, you may also want to remove some or all of the following files from the `rootfs` partition:

- `etc/wpa_supplicant/wpa_supplicant.conf`: Wi-Fi configuration and network secrets
- `home/pi/.ssh/authorized_keys`: SSH public keys authorized to remotely connect to the PlanktoScope
- `home/pi/data/`: all images acquired before by the PlanktoScope - this directory may be large, and you probably don't want to copy those datasets across all your other PlanktoScopes.
- `home/pi/.*history`: Bash and Python history
- `home/pi/.gitconfig`: Git configuration, which may contain user-specific details.

!!! info
    You can also delete the files listed above before running the `/usr/libexec/prepare-custom-image` script; the effect is the same. Either way, those files will be permanently deleted on your SD card. However, if you want to keep those files on your SD card, you should make backup copies of those files, and then you can copy those files back onto your SD card after you finish cloning the SD card to an image.

Next, proceed to the [Make an SD card image](#make-an-sd-card-image) sections of this guide.

### Prepare an exact backup

If you want to make an exact backup of your SD card, and you don't want to reuse your SD card image across multiple PlanktoScopes, then you shouldn't run the `/usr/libexec/prepare-custom-image` script, as that script will delete some files which you probably want to keep; instead, you just should run the following commands:

```
sudo systemctl stop overlay-etc.service
rm /var/lib/overlays/overrides/etc/init.d/resize2fs_once
rm /var/lib/overlays/overrides/etc/rc3.d/S01resize2fs_once
sudo shutdown now
```

Next, you should remove the SD card from your PlanktoScope and plug it into another computer, so that you can clone the SD card into an SD card image; this guide assumes that your other computer runs Linux. Then proceed to the [Make an SD card image](#make-an-sd-card-image) section of this guide.

## Make an SD card image

### Locate the SD card

Now that your SD card is plugged into a Linux computer, you will need to determine the path of the device which represents it. Usually it will look something like `/dev/sda`, `/dev/sdb`, `/dev/mmcblk0`, or some other path in `/dev`. To find the device, run the command `sudo fdisk -l` in your terminal. The output may look something like:

```
Disk /dev/mmcblk0: 58.29 GiB, 62587404288 bytes, 122241024 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xa2033091
```

To determine which disk device corresponds to your SD card, you should check the size of each device to find the one which approximately matches the size of your SD card.

Next, you should unmount the SD card from your system (or ensure that the device is already not mounted on your system). If you're unsure whether the SD card is mounted, you should use the `umount` command. For example, if your device is `/dev/mmcblk0`, you will need to run:

```
sudo umount /dev/mmcblk0p1
sudo umount /dev/mmcblk0p2
```

If the devices were already not mounted, you should expect to see (and you can safely ignore) error messages which look like:

```
umount: /dev/mmcblk0p1: not mounted.
umount: /dev/mmcblk0p2: not mounted.
```

### Clone the SD card to an image

To clone the Raspberry Pi's SD card to an image file which you can write to other SD cards, you should follow the instructions at <https://github.com/mgomesborges/raspberry-pi/blob/master/setup/clone-sd-card.md> or <https://raspberrytips.com/create-image-sd-card/> . For example, if you are using a Linux computer and the SD card shows up as `/dev/mmcblk0`, you could run the following command (replacing file paths and names accordingly):

```
sudo dd bs=4M if=/dev/mmcblk0 of=/some/path/here/image-name-here.img status=progress
```

This will create a `.img` file (at `/some/path/here/image-name-here.img`) as large as your SD card - make sure you have enough space on your hard drive for the file! If your SD card is large, this process may take a long time; this greatly depends on the speed of your SD card reader. For example, a slow SD card reader may take 30 minutes in order to clone a 32 GB SD card.

### Shrink the SD card image

In order to make the SD card practical to share, you should shrink and compress the SD card image file using the [PiShrink tool](https://github.com/Drewsif/PiShrink). For example, on Linux you could run the following set of commands (again replacing file paths and names accordingly):

```
cd /some/path/here
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
sudo ./pishrink.sh -za image-name-here.img
```

If you had set up the PlanktoScope software on a Raspberry Pi OS Lite image, you should get a `image-name-here.img.gz` file which is at least 2 GB in size.

## Use the SD card image

You can now use this SD card image with the [non-standard installation guide](../setup/software/nonstandard-install.md) for installing the PlanktoScope OS on an SD card for one or more PlanktoScopes.
