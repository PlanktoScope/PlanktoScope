# software

This directory will eventually contain various units of software related to the PlanktoScope software distribution; note that specific programs may be managed in separate repositories. Currently, this directory only contains a manual setup script (`distro/setup/setup.sh`) which you can run on a Raspberry Pi in order to set up the PlanktoScope software distribution on it.

## Usage

### Setup

For setup instructions, please refer to the [non-standard installation guide](../documentation/docs/setup/software/nonstandard-install.md) for the PlanktoScope software.

### SD card cloning

If you would like to clone the Raspberry Pi's SD card to an image file which you can write to other SD cards, you should follow the instructions at https://github.com/mgomesborges/raspberry-pi/blob/master/setup/clone-sd-card.md or https://raspberrytips.com/create-image-sd-card/ . For example, if you are using a Linux computer and the SD card shows up as `/dev/mmcblk0`, you could run the following command (replacing file paths and names accordingly):

```
sudo dd bs=4M if=/dev/mmcblk0 of=/some/path/here/image-name-here.img
```

This will create a `.img` file as large as your SD card - make sure you have enough space on your hard drive for the file! You can then shrink and compress the file using the [PiShrink tool](https://github.com/Drewsif/PiShrink). For example, on Linux you could run the following set of commands (again replacing file paths and names accordingly):

```
cd /some/path/here
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
sudo ./pishrink.sh -za image-name-here.img
```

If you had set up the PlanktoScope software on a Raspberry Pi OS Lite image, you should get a `image-name-here.img.gz` file which is approximately 1 GB in size.
