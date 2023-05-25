# PlanktoScope Simple Setup Guide

![easy install](../images/software/IMG_1532.jpg)

## Download the image

For ease of setup, a preconfigured image is provided. You can download it from [s3.bazile.io/planktoscope/images/planktoscope-v2.3-final.img.gz](https://s3.bazile.io/planktoscope/images/planktoscope-v2.3-final.img.gz).

```sh
wget s3.bazile.io/planktoscope/images/planktoscope-v2.3-final.img.gz
```

## Writing the image to the SD card

### Using balenaEtcher

1. Download and install [balenaEtcher](https://www.balena.io/etcher/).
2. Connect an SD card reader with the micro SD card inside.
3. Open balenaEtcher and select from your hard drive the previously downloaded img file file you wish to write to the SD card.
4. Select the SD card you wish to write your image to.
5. Review your selections and click 'Flash!' to begin writing data to the SD card.

### Using ddrescue

If you prefer a command line tool, you can also use ddrescue instead of balenaEtcher.

#### Install ddrescue on apt based distributions

```sh
sudo apt install -y gddrescue
```

#### Uncompress the image

```sh
gunzip planktoscope-v2.3-final.img.gz
```

#### Write the image to the SD-Card

```sh
sudo ddrescue planktoscope-v2.3-final.img /dev/mmcblk0 --force
```

!!! warning

    Be extremely careful when choosing the storage medium and check if you really use the device path of the memory card. Once the image has been written, these data blocks cannot be recovered.

## Inserting the SD card

Once flashing is over, you can unmount the SD card from the computer (usually done by right clicking on the card icon in the taskbar).

Insert now the card in the Raspberry installed in your PlanktoScope.

## Install a mDNS client

To access the PlanktoScope services through your browser, you need to install a mDNS client.

If you are running a linux machine, you are in luck. Avahi-client is probably already installed on your machine. Check with your package manager.

If you are running a Windows machine, you will need to install the Bonjour service. It's a client developped by Apple. However, if you already use iTunes, Skype or even Photoshop, you may already have a client installed. Try skipping to the next step. If you can't access the linked page, come back here!

To install the client, download the installer [here](https://download.info.apple.com/Mac_OS_X/061-8098.20100603.gthyu/BonjourPSSetup.exe) and launch it.

## Start playing

Start up your PlanktoScope and connect to its WiFi network. You can now access the webpage at <http://planktoscope.local:1880/ui> to start using your machine!
