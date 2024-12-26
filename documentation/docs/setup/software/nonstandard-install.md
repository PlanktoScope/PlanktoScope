# Non-Standard Installation

This page provides instructions for setting up non-standard versions of the PlanktoScope OS on a PlanktoScope. The PlanktoScope project also uses this same process for creating the official PlanktoScope software SD card images used in the [standard software installation process](standard-install.md).

## Prerequisites

This guide assumes that:

1. You have previous experience with using the command-line terminal on the Raspberry Pi OS or another Linux distribution.
2. You have already confirmed that your PlanktoScope works without any problems with software installed by the standard PlanktoScope software setup process.
3. You already know how to use the PlanktoScope software.

If you have not used the PlanktoScope software before, you should first start with the standard software setup process in order to troubleshoot any problems with your PlanktoScope hardware; you can then try the non-standard setup process afterwards.

In order to complete the non-standard setup process, you will need all of the following:

1. A Raspberry Pi computer. We only test to ensure that the PlanktoScope software works on the Raspberry Pi 4; it may or may not work on the Raspberry Pi 3, and it does not yet work on the Raspberry Pi 5.
2. A keyboard connected to your Raspberry Pi.
3. A display connected to your Raspberry Pi.
4. A micro-SD card for your Raspberry Pi.
5. A way to provide internet access to your Raspberry Pi.
6. A separate computer which can flash SD card images to your micro-SD card.

## Install and set up Raspberry Pi OS on your Raspberry Pi

### Download a Raspberry Pi OS SD card image

The setup scripts for the PlanktoScope OS assume that you will be setting up the PlanktoScope software on a 64-bit version of the Raspberry Pi OS with Debian version 11 (bullseye), preferably the version released on 2023-03-12. You can choose any of the following three variants of that version of the Raspberry Pi OS, depending on your needs:

- ["Raspberry Pi OS with desktop"](https://downloads.raspberrypi.com/raspios_oldstable_arm64/images/raspios_oldstable_arm64-2024-03-12/2024-03-12-raspios-bullseye-arm64.img.xz)
- ["Raspberry Pi OS with desktop and recommended software"](https://downloads.raspberrypi.com/raspios_oldstable_full_arm64/images/raspios_oldstable_full_arm64-2024-03-12/2024-03-12-raspios-bullseye-arm64-full.img.xz)
- ["Raspberry Pi OS Lite"](https://downloads.raspberrypi.com/raspios_oldstable_lite_arm64/images/raspios_oldstable_lite_arm64-2024-03-12/2024-03-12-raspios-bullseye-arm64-lite.img.xz)

The standard PlanktoScope software SD card images are built on the Raspberry Pi OS Lite image, which only provides a command-line interface, without a graphical desktop environment or web browser; because the PlanktoScope's graphical user interface must be accessed from a web browser, you might prefer to use the "Raspberry Pi OS with desktop" image in order to have a graphical desktop environment with a web browser. This would allow you to operate the PlanktoScope by plugging in a display, keyboard, and mouse to your Raspberry Pi; otherwise, you will have to connect to the PlanktoScope from another device over Ethernet or Wi-Fi in order access the PlanktoScope's graphical user interface.

!!! warning

    The latest version of Raspberry Pi OS, with Debian version 12 (bookworm), can be downloaded from [the Raspberry Pi Operating system images page](https://www.raspberrypi.com/software/operating-systems/), but the PlanktoScope software setup scripts do not yet work on Debian version 12; that page also has links named "Archive" under the download buttons where you can find older versions with Debian version 11 (bullseye) under the "Raspberry Pi OS (Legacy)" section; those links are the same as the links we listed above.

### Write the OS image to an SD card

Next, you will need to write your downloaded Raspberry Pi OS image file to your microSD card. Plug your microSD card into your computer; you may need to use a microSD-to-SD-card adapter, and/or an SD-card-to-USB adapter.

To use a graphical application to write the image file to your microSD card, you can install the Raspberry Pi imager. Download the latest version of the [Raspberry Pi Imager](https://www.raspberrypi.com/software/), install it, and start it. Select the Raspberry Pi OS image file (likely a `.img`, `.img.gz`, or `.img.xz` file) you just downloaded, and select the SD card you want to write the Raspberry Pi OS image to. Review your selections and click the appropriate button to begin writing the Raspberry Pi OS image to the SD card. The process should take several minutes.

If you'd instead prefer to write the image file to your microSD card from a command-line tool, you could instead use a tool like `ddrescue` on a Debian-based system, e.g. as follows:

```
gunzip planktoscope-v2.3-final.img.gz
sudo ddrescue planktoscope-v2.3-final.img /dev/mmcblk0 --force
```

Warning: be extremely careful when choosing the storage medium and ensure that you are writing the OS image file to the device which actually corresponds to the correct microSD card. Once the image has been written, data previously on the device will be lost and impossible to recover.

### Configure your Raspberry Pi

Insert the microSD card into your Raspberry Pi and connect your Pi to a screen, a mouse, and a keyboard. Double-check the connections before plugging in power.

The first boot to the desktop may take up to 120 seconds. This is normal and is caused by the image expanding the filesystem to the whole SD card. DO NOT REBOOT before you reach the desktop.

Eventually, the display will ask you to configure some settings for the Raspberry Pi. You will be asked to choose language settings and a keyboard layout; you should choose settings appropriate for you. The standard PlanktoScope SD card images use the `en_US.UTF-8` locale and the "Generic 104-key PC, English (US)" keyboard layout. The display will also ask you to set a username and password for the default user account on the Raspberry Pi; you *must* choose `pi` as the username, and you should choose a password you can remember. By default, the standard PlanktoScope SD card images use `copepode` as the password - so you may want to choose a different password for better security. Refer to the official [Getting Started with your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/) guide for additional details and instructions on configuring settings for the Raspberry Pi.

Next, configure your Raspberry Pi to get internet access - your Raspberry Pi will need to download software packages from the internet as part of the installation process for the PlanktoScope OS. If you have an Ethernet cable you can plug into your Raspberry Pi, that will be the simplest option for setup, because it won't require you to edit any files or run any commands on your Raspberry Pi; when we make our official SD card images with the PlanktoScope OS, we use an Ethernet cable. Otherwise, you will need to connect your Raspberry Pi to a wifi network with internet access; you can refer to the Raspberry Pi project's [network configuration guide](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-networking).

## Set up the PlanktoScope OS

### Run the installation script

Depending on whether you're installing the software on a PlanktoScope with the PlanktoScope HAT (which is the standard HAT on v2.3 hardware and later) or with the Adafruit Stepper Motor HAT (which is the standard HAT on v2.1 hardware), you will need to adjust the commands below. Specifically, if you're installing the software for a PlanktoScope with the Adafruit Stepper Motor HAT, you will need to replace the word `planktoscopehat` with the word `adafruithat` in any of the commands below.

Log in to your Raspberry Pi and (if you installed a version of Raspberry Pi OS with a graphical desktop) open a terminal. Then type in one of the following commands, depending on which release channel you want to use for installation (refer to our [technical reference document on release channels](../../reference/software/release-process.md#release-channels) to understand which release channel to use):

=== "Stable"

    ```
    wget -O - https://install.planktoscope.community/distro.sh \
      | sh -s -- -v software/stable -H planktoscopehat
    ```
    
    This will install the most recent stable release of the PlanktoScope OS (or, if the most recent release of the PlanktoScope software is a stable release, to install that stable release). This is recommended for most users.

=== "Beta"

    ```
    wget -O - https://install.planktoscope.community/distro.sh \
      | sh -s -- -v software/beta -H planktoscopehat
    ```
    
    This will install the most recent beta prerelease of the PlanktoScope OS (or, if the most recent prerelease/release of the PlanktoScope software is a stable release, to install that stable release). The beta prerelease probably contains bugs which will be fixed before the next stable release.

=== "Edge"

    ```
    wget -O - https://install.planktoscope.community/distro.sh \
      | sh -s -- -v master -H planktoscopehat
    ```
    
    This will install the current unstable development version of the PlanktoScope OS. This version is likely to be broken in various ways.

Instead of installing the latest version on the "stable", "beta", or "edge" release channel, you can also install a specific tagged release or pre-release of the PlanktoScope software. For example, to install the *v2024.0.0-alpha.1* pre-release of the PlanktoScope software, you would run the following command:

```
wget -O - https://install.planktoscope.community/distro.sh \
  | sh -s -- -t tag -v v2024.0.0-alpha.1 -H planktoscopehat
```

You can also choose to install the PlanktoScope software from some other repository on GitHub instead of [github.com/PlanktoScope/PlanktoScope](https://github.com/PlanktoScope/PlanktoScope), by using the `-r` command-line option; for more information including usage examples, you can refer to the reference page for [the installation script's command-line parameters](../../reference/software/subsystems/installation.md#script-parameters), and/or you can get usage instructions by running the following command:

```
wget -O - https://install.planktoscope.community/distro.sh \
  | sh -s -- --help
```

### Wait for installation to finish

The installation process will take a long time (around 15 - 30 minutes, depending on the speed of your internet connection and your microSD card) to finish.

If an error occurs during this setup process, you will need to wipe the Raspberry Pi's microSD card, flash the Raspberry Pi OS image onto it again, and try running the setup steps again. Otherwise, you will eventually see a message reporting that the setup script finished setting up the PlanktoScope application environment. Afterwards, you will need to restart the Raspberry Pi, e.g. with the following command:

```
sudo reboot now
```

This step is necessary to finish the PlanktoScope software setup process.

After your PlanktoScope reboots, the display connected to your PlanktoScope should show a login prompt with the format `pkscope-{machine-name} login:` , where `{machine-name}` is substituted with your PlanktoScope's machine name. For example, if the login prompt says `pkscope-chain-list-27764 login:`, then the PlanktoScope's machine name is `chain-list-27764`. You should write a note somewhere with this machine name, for future reference.

!!! info

    Recording the PlanktoScope's machine name in a note (or on your PlanktoScope) will be especially important if you might have multiple PlanktoScopes in the future or if you might need to access the PlanktoScope via an indirect connection (e.g. from a device connected to the same network router as the PlanktoScope). This is because the machine name is used for naming the Wi-Fi hotspot made by your PlanktoScope and for generating a machine-specific URL for accessing your PlanktoScope.

!!! tip

    If you are unhappy with the auto-generated machine name, you can override it with a custom name. Refer to our instructions for [changing the machine name](../../operation/networking.md#change-the-machine-name) in our networking operations guide, but first see the notes at the top of that guide.

## Connect to the PlanktoScope

Afterwards, your PlanktoScope's Raspberry Pi will either connect to a Wi-Fi network (if you had previously configured it to connect to a Wi-Fi network) or make its own Wi-Fi hotspot, whose name has format `pkscope-{machine-name}` (where `{machine-name}` should be substituted with your PlanktoScope's specific machine name, which you should have recorded in a note in the previous step), and whose password is `copepode`.

You will only be able to access the PlanktoScope's graphical user interface by plugging in a display and keyboard and mouse to the Raspberry Pi if you had previously used a "Raspberry Pi OS with desktop" or "Raspberry Pi OS with desktop and recommended software" SD card image as the base for the PlanktoScope software's setup script. In that case, you can open a web browser window on the Raspberry Pi and open <http://localhost> or any of the URLs listed in the [standard installation guide](./standard-install.md#connect-to-the-planktoscope). Otherwise:

- If you plan to connect another device directly to your PlanktoScope via its Wi-Fi hotspot or via an Ethernet cable, follow the same instructions for connecting to your PlanktoScope as in the [standard installation guide](./standard-install.md#connect-to-the-planktoscope).

- If you had previously configured your PlanktoScope's Raspberry Pi to connect to a Wi-Fi network, it will not make its own Wi-Fi hotspot. On the Wi-Fi network it's connected to, it will only be accessible by its machine-specific mDNS URL,  which has the format `http://pkscope-{machine-name}.local`, where `{machine-name}` should be replaced by your PlanktoScope's specific machine name (which you should have recorded in the previous step).

## Next steps

Now that you have installed the software and accessed the PlanktoScope software's user interface from your web browser, you should proceed to our guide for [configuring your PlanktoScope](config.md).
