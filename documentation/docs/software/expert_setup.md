# Expert Setup

This page provides instructions for setting up non-standard versions of the PlanktoScope software distribution on a PlanktoScope.

## Install and setup Raspberry Pi OS on your Raspberry Pi

### Download the Raspberry Pi OS image

The setup scripts for the PlanktoScope software distribution assume that you will be setting up the PlanktoScope software on a 32-bit version of the Raspberry Pi OS. The latest version of Raspberry Pi OS can always be downloaded from [the Raspberry Pi Operating system images page](https://www.raspberrypi.com/software/operating-systems/). Instead, you should choose between the "Raspberry Pi OS with desktop", "Raspberry Pi OS with desktop and recommended software", or "Raspberry Pi OS Lite" options, depending on your needs. The standard PlanktoScope software SD card images are built on the Lite image, which only provides a command-line interface, without a graphical desktop environment; you might prefer to use the "Raspberry Pi OS with desktop" image in order to have a graphical desktop environment.

### Write the OS image to an SD card

Next, you will need to write your downloaded Raspberry Pi OS image file to your microSD card. Plug your microSD card into your computer; you may need to use a microSD-to-SD-card adapter, and/or an SD-card-to-USB adapter.

To use a graphical application to write the image file to your microSD card, you can install balenaEtcher or the Raspberry Pi imager. Download the latest version of [balenaEtcher](https://www.balena.io/etcher/) or the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and install it. Then open balenaEtcher or the Raspberry Pi Imager. Select the Raspberry Pi OS image file (likely a `.img`, `.img.gz`, or `.img.xz` file) you just downloaded, and select the SD card you want to write the Raspberry Pi OS image to. Review your selections and click the "Flash!" or "Write" button to begin writing the Raspberry Pi OS image to the SD card. The process should take several minutes.

If you'd instead prefer to write the image file to your microSD card from a command-line tool, you could instead use ddrescue on a Debian-based system, e.g. as follows:
```
gunzip planktoscope-v2.3-final.img.gz
sudo ddrescue planktoscope-v2.3-final.img /dev/mmcblk0 --force
```
Warning: be extremely careful when choosing the storage medium and ensure that you are writing the OS image file to the device which actually corresponds to the correct microSD card. Once the image has been written, data previously on the device will be lost and impossible to recover.


### Configure your Raspberry Pi

Insert the microSD card into your Raspberry Pi and connect your Pi to a screen, a mouse, and a keyboard. Double-check the connections before plugging in power.

The first boot to the desktop may take up to 120 seconds. This is normal and is caused by the image expanding the filesystem to the whole SD card. DO NOT REBOOT before you reach the desktop.

Eventually, the display will ask you to configure some settings for the Raspberry Pi. You will be asked to choose language settings and a keyboard layout; you should choose settings appropriate for you. The display will also ask you to set a username and password for the default user account on the Raspberry Pi; you *must* choose `pi` as the username, and you should choose a password you can remember. By default, we use `copepode` as the password - so you may want to choose a different password for better security. Refer to the official [Getting Started with your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/) guide for additional details and instructions on configuring settings for the Raspberry Pi.

Next, configure your Raspberry Pi to get internet access - your Raspberry Pi will need to download software packages from the internet as part of the installation process for the PlanktoScope software distribution. If you have an Ethernet cable you can plug into your Raspberry Pi, that will be the simplest option for setup, because it won't require you to edit any files or run any commands on your Raspberry Pi; when we make our official SD card images with the PlanktoScope software distribution, we use an Ethernet cable. Otherwise, you will need to connect your Raspberry Pi to a wifi network with internet access; you can find instructions for how to do so at <https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-networking>

## Install the PlanktoScope software distribution

Log in to your Raspberry Pi and (if you installed a version of Raspberry Pi OS with a graphical desktop) open a terminal. Then type in each of the following commands:

```
cd /home/pi
wget https://github.com/PlanktoScope/PlanktoScope/archive/refs/heads/stable.zip
unzip stable.zip
rm stable.zip
mv PlanktoScope-stable /home/pi/PlanktoScope
```

This will prepare you to install the latest stable release of the PlanktoScope software distribution; if you need to install some other release such as `beta` or `edge`, you will need to change the names accordingly in the commands above. Then you will run one of the two following commands, depending on whether your PlanktoScope has the Adafruit Stepper HAT or the custom PlanktoScope HAT:

```
/home/pi/PlanktoScope/software/distro/setup/setup.sh adafruithat
```

```
/home/pi/PlanktoScope/software/distro/setup/setup.sh pscopehat
```

The setup script will take a long time (at least 30 minutes, depending on the speed of your internet connection) to complete.

If an error occurs during this setup process, you will need to wipe the Raspberry Pi's microSD card, flash the Raspberry Pi OS image onto it again, and try running the setup steps again. Otherwise, you will eventually see a message reporting that the setup script finished setting up the PlanktoScope application environment. Then you should restart the Raspberry Pi, e.g. with the following command:

```
sudo reboot now
```

## Connect to the PlanktoScope

Afterwards, your PlanktoScope's Raspberry Pi will either connect to a wifi network (if you had previously configured it to connect to a wifi network) or make its own local isolated wifi network. If you connect another device (e.g. a phone or computer) to the PlanktoScope's Raspberry Pi over its local isolated wifi network or over an Ethernet cable, then you can open a web browser on the device to access the PlanktoScope's dashboard at one of the following URLs (try them in the following order, and just use the first one which works):

- <http://home.planktoscope> (this should work unless your web browser is configured to use a Private DNS provider)
- <http://planktoscope.local> (this should work unless you're on a device and web browser without mDNS support; notably, Google Chrome on Android does not have mDNS support)
- <http://192.168.4.1> (this should always work)
- <http://192.168.5.1> (this should always work)
