# How to create a new SD master card, or backup efficiently your existing card

If you want to backup your machine, or prepare an image from the golden machine to share it to the world (or your students), you may want to follow those steps.

!!! tip
The golden machine is the machine on which the setup is made. Everything is prepared according to your needs. Once it's ready, you just cleanly shut it down, pop the SD card out, and copy it to share the love!

Everything in this guide is written by using a Linux computer in which the sdcard is inserted.

## Find and unmount your sd card

Firsts things firsts, we need to know where is our sdcard in the linux filesystem.

To find the device, open a terminal and type in `sudo fdisk -l`.

In the output, there will be a section looking like this:

```txt
Disk /dev/mmcblk0: 58.29 GiB, 62587404288 bytes, 122241024 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xa2033091
```

There is a very high probability that the device name we are looking for starts with `mmcblk`. To make sure this is the device we are looking for, use the size displayed (in this case, it is a 64GB sdcard).

We are now going to make sure the device is not mounted on your system (some OSes mount inserted sdcards automatically).

Simply type `sudo umount /dev/mmcblk0p1` and `sudo umount /dev/mmcblk0p2` to unmount the disk.

If the devices were not mounted, you may see an error message that you can ignore. The message looks like this:

```txt
umount: /dev/mmcblk0p2: not mounted.
```

## Copy the sdcard to your disk

Choose and navigate to an appropriate directory on your computer.

We are going to use `dd` to copy the sdcard. The command to type is the following:

```sh
sudo dd if=/dev/mmcblk0 of=planktoscopeimage.img bs=4M status=progress
```

- `if`: stands for `input file`, this is the input that we want to copy FROM
- `of`: stands for `output file`, this is where the image is going to be written
- `bs`: chooses a block size of 4M, this helps to speeds up the copy
- `status`: just display a progression of the copy

The copy may take more than 15 minutes to complete, so you can go get a coffee or something.

Congratulations, you now have a complete copy of your sdcard!

However it's big. Huge even. We are going to resize it to make its storage and sharing easier.

## Shrink and share

Before shrinking the image, let's sanitize it first and remove eventual secrets stored in it (like wifi passwords for example).

```sh
mkdir mnt
sudo mount -o loop,rw,offset=$((532480 * 512)) planktoscopeimage.img ./mnt/
```

You can now cleanup the image. The `mnt` directory is the same as the root of your sdcard. You should find your way from there.

Notably, do not forget to edit/remove the following files:

- `mnt/etc/wpa_supplicant/wpa_supplicant.conf`: wifi configuration and network secrets
- `mnt/home/pi/.ssh/authorized_keys`: public ssh keys authorized to connect to this planktoscope
- `mnt/home/pi/data/`: this folder has all the images taken before by your machine, you may want to clean it up too
- `mnt/home/pi/.*history`: bash and python history
- `mnt/home/pi/.gitconfig`: git config

!!! info
If you want to distribute the image you created, you need to start the service that will recreate the host ssh keys on startup:
`sudo ln -s /lib/systemd/system/regenerate_ssh_host_keys.service etc/systemd/system/multi-user.target.wants/regenerate_ssh_host_keys.service`

Once your cleanup is done, unmount the image with `sudo umount mnt`.

Now, let's shrink the image! To do so, we are going to use [PiShrink](https://github.com/Drewsif/PiShrink).

You can install the script using the following:

```sh
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
```

Now, starts PiShrink on your image, and watch it do its magic:

```sh
sudo ./pishrink.sh -z -a planktoscopeimage.img
```

The flags `-z -a` are used to compress the image to a gz file using the multithread version of gzip (pigz).

!!! info
If you want to distribute the image you created, you should use the flag `-p` with PiShrink to remove logs, apt archives, ssh hosts keys and similar things.

You now have a compressed image that should be between 10 and 100 times smaller than the one you started with. You can distribute it (don't forget to do the steps above first), archive it, do whatever you please with it!
