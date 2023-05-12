# software

This directory will eventually contain various units of software related to the PlanktoScope software distribution; note that specific programs may be managed in separate repositories. Currently, this directory only contains a manual setup script (`distro/build/build.sh`) which you can run on a Raspberry Pi in order to set up the PlanktoScope software distribution on it.

## Usage

First, flash your microSD card with the standard (32-bit) version of Raspberry Pi OS; we recommend using the Raspberry Pi OS Lite (32-bit) variant unless you plan to operate the PlanktoScope with an attached display, mouse, and keyboard. You can find further instructions at https://www.raspberrypi.com/software/

Next, insert your microSD card into the Raspberry Pi, connect a display and keyboard for setup, and boot up the Raspberry Pi by plugging in the power cable (which should be a USB-C cable, assuming you have a Raspberry Pi 4 - which is strongly recommended). Eventually, the display will show prompts asking you to choose a keyboard layout; you should choose settings appropriate for you. The display will also ask you to set a username and password for the default user account on the Raspberry Pi; you should choose `pi` as the username, and you should choose a password you can remember. By default, we use `copepode` as the password - so you may want to choose a different password for better security.

Next, configure your Raspberry Pi to get internet access. If you have an Ethernet cable you can plug into your Raspberry Pi, that will be the simplest option for setup - when we make our official SD card images with the PlanktoScope software distribution, we use an Ethernet cable. Otherwise, you will need to connect to a wifi network with internet access; you can find instructions for how to do so at https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-networking

Next, log in to your Raspberry Pi and (if you installed a version of Raspberry Pi OS with a graphical desktop) open a terminal. Then type in each of the following commands:

```
cd /home/pi
wget https://github.com/PlanktoScope/PlanktoScope/archive/refs/heads/stable.zip
unzip stable.zip
rm stable.zip
mv PlanktoScope-stable PlanktoScope
```

This will prepare you to install the latest stable release of the PlanktoScope software distribution; if you need to install some other release such as `beta` or `edge`, you will need to change the names accordingly in the commands above. Then you will run the following command, which will take a long time to finish:

```
/home/pi/PlanktoScope/software/distro/build/build.sh
```

If an error occurs during this setup process, you will need to wipe the Raspberry Pi's microSD card, flash the Raspberry Pi OS image onto it again, and try running the setup steps again. Otherwise, you will eventually see a message reporting that the build script finished building the PlanktoScope application environment. Then you should restart the Raspberry Pi, e.g. with the following command:

```
sudo shutdown -r now
```

Afterwards, your PlanktoScope's Raspberry Pi will either connect to a wifi network (if you had previously configured it to connect to a wifi network) or make its own local isolated wifi network. If you connect another device (e.g. a phone or computer) to the PlanktoScope's Raspberry Pi over its local isolated wifi network or over an Ethernet cable, then you can open a web browser on the device to access the PlanktoScope's dashboard at one of the following URLs (try them in the following order, and just use the first one which works):

- http://home.planktoscope:1880/ui (if your web browser isn't configured to use a Private DNS provider)
- http://planktoscope.local:1880/ui (if you're on a device which supports mDNS)
- http://192.168.4.1:1880/ui (if you're connected over the PlanktoScope's isolated wifi network)
- http://192.168.5.1:1880/ui (if you're connected over Ethernet)
