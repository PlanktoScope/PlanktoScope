# Non-Standard Installation

This page provides instructions for installing non-standard versions of the PlanktoScope software distribution on a PlanktoScope. The PlanktoScope project also uses this same process for creating the official PlanktoScope software SD card images used the [standard software installation process](standard-install.md).

## Prerequisites

This guide assumes that:

1. You have previous experience with using the command-line terminal on the Raspberry Pi OS or another Linux distribution.
2. You have already confirmed that your PlanktoScope works without any problems with software installed by the standard PlanktoScope software setup process..
3. You already know how to use the PlanktoScope software.

If you have not used the PlanktoScope software before, you should first start with the standard software setup process in order to troubleshoot any problems with your PlanktoScope hardware; you can then try the non-standard setup process afterwards.

In order to complete the non-standard setup process, you will need all of the following:

1. A Raspberry Pi computer. We only test to ensure that the PlanktoScope software works on the Raspberry Pi 4; it may or may not work on the Raspberry Pi 3.
2. A keyboard connected to your Raspberry Pi.
3. A display connected to your Raspberry Pi.
4. A micro-SD card for your Raspberry Pi.
5. A way to provide internet access to your Raspberry Pi.
6. A separate computer which can flash SD card images to your micro-SD card.

## Install and set up Raspberry Pi OS on your Raspberry Pi

### Download a Raspberry Pi OS SD card image

The setup scripts for the PlanktoScope software distribution assume that you will be setting up the PlanktoScope software on a 32-bit version of the Raspberry Pi OS with Debian version 11 (bullseye), preferably the version released on 2023-05-03. The latest version of Raspberry Pi OS, with Debian version 12 (bookworm), can be downloaded from [the Raspberry Pi Operating system images page](https://www.raspberrypi.com/software/operating-systems/), but the setup scripts do not yet work on Debian version 12; that page also has links named "Archive" under the download buttons where you can find older versions with Debian version 11. You should choose between the ["Raspberry Pi OS with desktop"](https://downloads.raspberrypi.com/raspios_armhf/images/raspios_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf.img.xz), ["Raspberry Pi OS with desktop and recommended software"](https://downloads.raspberrypi.com/raspios_full_armhf/images/raspios_full_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-full.img.xz), or ["Raspberry Pi OS Lite"](https://downloads.raspberrypi.com/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz) options, depending on your needs.

The standard PlanktoScope software SD card images are built on the Raspberry Pi OS Lite image, which only provides a command-line interface, without a graphical desktop environment or web browser; because the PlanktoScope's graphical user interface must be accessed from a web browser, you might prefer to use the "Raspberry Pi OS with desktop" image in order to have a graphical desktop environment with a web browser. This would allow you to operate the PlanktoScope by plugging in a display, keyboard, and mouse to your Raspberry Pi; otherwise, you will have to connect to the PlanktoScope from another device over Ethernet or Wi-Fi in order access the PlanktoScope's graphical user interface.

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

Eventually, the display will ask you to configure some settings for the Raspberry Pi. You will be asked to choose language settings and a keyboard layout; you should choose settings appropriate for you. The standard PlanktoScope SD card images use the `en_US.UTF-8` locale and the "Generic 104-key PC, English (US)" keyboard layout. The display will also ask you to set a username and password for the default user account on the Raspberry Pi; you *must* choose `pi` as the username, and you should choose a password you can remember. By default, the standard PlanktoScope SD card images use `copepode` as the password - so you may want to choose a different password for better security. Refer to the official [Getting Started with your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/) guide for additional details and instructions on configuring settings for the Raspberry Pi.

Next, configure your Raspberry Pi to get internet access - your Raspberry Pi will need to download software packages from the internet as part of the installation process for the PlanktoScope software distribution. If you have an Ethernet cable you can plug into your Raspberry Pi, that will be the simplest option for setup, because it won't require you to edit any files or run any commands on your Raspberry Pi; when we make our official SD card images with the PlanktoScope software distribution, we use an Ethernet cable. Otherwise, you will need to connect your Raspberry Pi to a wifi network with internet access; you can find instructions for how to do so at <https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-networking>

## Set up the PlanktoScope software distribution

### Download the setup scripts

Log in to your Raspberry Pi and (if you installed a version of Raspberry Pi OS with a graphical desktop) open a terminal. Then type in each of the following commands, for either the latest beta prerelease of the PlanktoScope software distribution, the latest stable release, or the latest development version:

=== "latest beta"

    ```
    cd /home/pi
    wget https://github.com/PlanktoScope/PlanktoScope/archive/refs/heads/beta.zip
    unzip beta.zip
    rm beta.zip
    mv PlanktoScope-beta /home/pi/PlanktoScope
    ```
    
    This will prepare you to install the most recent beta prerelease of the PlanktoScope software distribution (or, if the most recent prerelease/release of the PlanktoScope software is a stable release, to install that stable release). The beta prerelease probably contains bugs which will be fixed before the next stable release.

=== "latest stable"

    ```
    cd /home/pi
    wget https://github.com/PlanktoScope/PlanktoScope/archive/refs/heads/stable.zip
    unzip stable.zip
    rm stable.zip
    mv PlanktoScope-stable /home/pi/PlanktoScope
    ```
    
    This will prepare you to install the most recent stable release of the PlanktoScope software distribution (or, if the most recent release of the PlanktoScope software is a stable release, to install that stable release). This is recommended for most users.

=== "development"

    ```
    cd /home/pi
    wget https://github.com/PlanktoScope/PlanktoScope/archive/refs/heads/master.zip
    unzip master.zip
    rm master.zip
    mv PlanktoScope-master /home/pi/PlanktoScope
    ```
    
    This will prepare you to install the current unstable development version of the PlanktoScope software distribution. This version is likely to be broken in various ways.

Instead of installing the latest beta, stable, or development version, you can also use GitHub to find the URL of a specific tagged version of the PlanktoScope software, and then you can download that and move the extracted directory to `/home/pi/PlanktoScope`; the standard PlanktoScope SD card images are generated with specific tagged versions. For example, to install the v2023.9.0-beta.1 prerelease of the PlanktoScope software, you would run the following commands:

```
cd /home/pi
wget https://github.com/PlanktoScope/PlanktoScope/archive/refs/tags/software/v2023.9.0-beta.1.zip
unzip v2023.9.0-beta.1.zip
rm v2023.9.0-beta.1.zip
mv Planktoscope-software-v2023.9.0-beta.1 /home/pi/PlanktoScope
```

### Run the setup scripts

Then you will run one of the two following commands, depending on whether your PlanktoScope hardware has the Adafruit Stepper HAT or the custom PlanktoScope HAT:

=== "Adafruit HAT"

    ```
    /home/pi/PlanktoScope/software/distro/setup/setup.sh adafruithat
    ```

=== "Custom PlanktoScope HAT"

    ```
    /home/pi/PlanktoScope/software/distro/setup/setup.sh pscopehat
    ```

The setup script will take a long time (at least 30 minutes, depending on the speed of your internet connection) to complete.

If an error occurs during this setup process, you will need to wipe the Raspberry Pi's microSD card, flash the Raspberry Pi OS image onto it again, and try running the setup steps again. Otherwise, you will eventually see a message reporting that the setup script finished setting up the PlanktoScope application environment.

## Connect to the PlanktoScope

Next, you will need to restart the Raspberry Pi, e.g. with the following command:

```
sudo reboot now
```

This step is necessary to finish the PlanktoScope software setup process.

Afterwards, your PlanktoScope's Raspberry Pi will either connect to a Wi-Fi network (if you had previously configured it to connect to a Wi-Fi network) or make a new isolated Wi-Fi network whose name starts with the word `pkscope` followed by the unique randomly-generated name of your PlanktoScope. If you connect another device (e.g. a phone or computer) directly to the PlanktoScope's Raspberry Pi over its isolated Wi-Fi network or over an Ethernet cable, then you can open a web browser on the device to access the PlanktoScope's graphical user interface at one of the following URLs (try them in the following order, and just use the first one which works):

- <http://home.pkscope> (this should work unless your web browser is configured to use a Private DNS provider)
- <http://pkscope.local> (this should work unless you're on a device and web browser without mDNS support; notably, older versions of Android do not have mDNS support)
- <http://192.168.4.1> (this should always work)
- <http://192.168.5.1> (this should always work)

Note that if you had previously configured your PlanktoScope's Raspberry Pi to connect to a Wi-Fi network, it will not make its own isolated Wi-Fi network. On the Wi-Fi network it's connected to, it should be accessible at <http://pkscope.local> (if you're accessing it from a device and web browser with mDNS support, assuming the device is on the same network), assuming that no other PlanktoScope is connected to the same network. If multiple PlanktoScopes are connected to the same network, open <http://pkscope.local> and read the web page's "Wrong PlanktoScope?" section for instructions on what URL to use; you can determine your PlanktoScope's name by connecting a display to its Raspberry Pi, booting up the Raspberry Pi, and reading the name from the login prompt (e.g. if it says `pkscope-chain-list-27764 login:`, then the PlanktoScope is named `pkscope-chain-list-27764`).

You will only be able to access the PlanktoScope's graphical user interface by plugging in a display and keyboard and mouse to the Raspberry Pi if you had previously used a "Raspberry Pi OS with desktop" or "Raspberry Pi OS with desktop and recommended software" SD card image as the base for the PlanktoScope software's setup script. In that case, you can open a web browser window on the Raspberry Pi and open <http://localhost> or any of the previously-listed URLs.

## Next steps

Now that you have installed the software and accessed the PlanktoScope software's user interface from your web browser, you should proceed to our guide for [configuring your PlanktoScope](config.md).
