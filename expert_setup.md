# Expert Setup

## Install and setup Raspbian on your Raspberry Pi

### Computer setup
In order to make it easy to connect to the PlanktoScope, you may want to install [avahi](https://en.wikipedia.org/wiki/Avahi_%28software%29) or the [Bonjour](https://en.wikipedia.org/wiki/Bonjour_%28software%29) service on any computer you will use to access the PlanktoScope interface. This will allow you to connect to the PlantoScop using an address similar such as http://planktoscope.local instead of an IP address.

### Download the image

The latest Raspbian version can always be downloaded from [the Raspberry Pi Downloads page](https://www.raspberrypi.org/downloads/raspbian/).
For a first build, it's recommende to download an image of Raspbian Buster with desktop.

#### Writing an image to the SD card

Download the latest version of [balenaEtcher](https://www.balena.io/etcher/) and install it.

Connect an SD card reader with the micro SD card inside.

Open balenaEtcher and select from your hard drive the image zip file you just downloaded.

Select the SD card you want to write your image to.

Review your selections and click `Flash!` to begin writing data to the SD card.

#### Prepare your Raspberry Pi
[Getting Started with your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/)

Plug the SD Card in your Raspberry Pi and connect your Pi to a screen, mouse and a keyboard. Check the connection twice before plugging the power.

The first boot to the desktop may take up to 120 seconds. This is normal and is caused by the image expanding the filesystem to the whole SD card. DO NOT REBOOT before you reach the desktop.

#### Finish the setup

Make sure you have access to internet and update/upgrade your fresh Raspbian install.

Update your Pi first. Open up a terminal, and do the following:
```sh
sudo apt update -y
sudo apt full-upgrade -y
sudo apt install git
```

You can now reboot your Pi safely.
```sh
sudo reboot now
```

## Raspberry Pi configuration

### Clone this repository!

First of all, and to ensure you have the latest documentation available locally, you should clone this repository using git.

Simply run the following in a terminal:
```sh
git clone https://github.com/PlanktonPlanet/PlanktoScope/
```

### Enable Camera/SSH/I2C in raspi-config

You can now launch the configuration tool:
```sh
sudo raspi-config
```

While you're here, a wise thing to do would be to change the default password for the `pi` user. This is very warmly recommended if your PlanktoScope is connected to a shared network you do not control. Just select the first option `1 System Options`, the `S3 Password`.

You may also want to change the default hostname of your Raspberry. To do so, choose option `1 System Options` then `S4 Hostname`. Choose a new hostname. We recommend using `planktoscope` as this name will then appear.

We need to activate a few things for the PlanktoScope to work properly.

First, we need to activate the camera interface. Choose `3 Interface Options`, then `P1 Camera` and `Yes`.

Now, you can go to `3 Interface Options`, then `P2 SSH`. Choose `Yes` to activate the SSH access.

Again, select `3 Interface Options`, then `P4 SPI`. Choose `Yes` to enable the SPI interface.

One more, select `3 Interface Options`, then `P5 I2C`. Choose `Yes` to enable the ARM I2C interface of the Raspberry.

Finally, select `3 Interface Options`, then `P6 Serial`.

This time, choose `No` to deactivate the login shell on the serial connection, but then choose `Yes` to keep the Serial port hardware enabled.

Last steps we need to do is to increase the amount of memory available to the GPU. Select `4 Performance Options`, then `P2 GPU Memory`. Write `256` in the field and choose OK.

Also, to be able to use the ISO8601 datetime standard, we need to change the locale in use. Choose `5 Localisations Options`, then `L1 Locale` and press space after selecting the `en_DK.UTF8`. Press Enter and then select the en_DK locale as default for your system.

!!!info
    The en_DK is a hack where month and day names are in English, but date and time format uses the ISO8601 format. See https://serverfault.com/questions/17118/how-do-i-set-the-date-format-to-iso-globally-in-linux

These steps can also be done from the Raspberry Pi Configuration GUI tool that you can find in `Main Menu > Preferences`. Go to the `Interfaces` tab. Pay attention, here the Serial Port must be enabled, but the Serial Port Console must be disabled.

!!! tip
    Optional step: overclocking
    It's possible to overclock the machine and get a bit more performance out of it. Open `/boot/config.txt` with `sudo nano /boot/config.txt` and add at the end of the file on two new lines:
    
    `over_voltage=6`

    `arm_freq=2000` 
    
    Those settings were verified to be stable, but if you notice any weird behavior under a high load, remove those lines.


Reboot your Pi safely.
```sh
sudo reboot now
```

## Install the needed libraries for the PlanktoScope

Most of the following happens in a command line environment. If you are using the desktop, please start a terminal emulator.

You can also connect to your PlanktoScope by using ssh using `ssh pi@planktoscope.local`.

You can then run the following to make sure your Raspberry has the necessary components to install and build everything it needs and to create the necessary folders:

```sh
sudo apt install build-essential python3 python3-pip
sudo update-alternatives --install $(which python) python $(readlink -f $(which python2)) 1
sudo update-alternatives --install $(which python) python $(readlink -f $(which python3)) 2
sudo update-alternatives --config python
# Choose line 0
mkdir test libraries
```

### Install all python libraries
To simplify setup, we provide requirements.txt:
```sh
pip3 install -U -r /home/pi/PlanktoScope/requirements.txt
```


### Add to python path
We need to do this to make sure we can call the modules from any path in the system, and not just from the `scripts` folder:

```
ln -s /home/pi/PlanktoScope/scripts/planktoscope /home/pi/.local/lib/python3.7/site-packages/planktoscope
ln -s /home/pi/PlanktoScope/scripts/shush /home/pi/.local/lib/python3.7/site-packages/shush
sudo mkdir -p /root/.local/lib/python3.7/site-packages
sudo ln -s /home/pi/PlanktoScope/scripts/planktoscope /root/.local/lib/python3.7/site-packages/planktoscope
sudo ln -s /home/pi/PlanktoScope/scripts/shush /root/.local/lib/python3.7/site-packages/shush
```

### [ADAFRUIT VERSION] Check CircuitPython's install
Start by following [Adafruit's guide](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi). You can start at the chapter `Install Python Libraries`.

#### Testing the installation and the wiring

It is recommended to test this setup by creating this small script under the name `test/blinkatest.py` and running it (you can use the editor nano if you are using the terminal). If you are using the image provided, you may find that the script is already there.

```python
#!/usr/bin/python3
import board
import digitalio
import busio


print("Hello blinka!")

# Try to great a Digital input
pin = digitalio.DigitalInOut(board.D4)
print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

print("done!")
```

To start the script, just run the following:
```sh
chmod +x test/blinkatest.py
./test/blinkatest.py
```

The output should be similar to this:
```sh
pi@planktoscope:~ $ ./test/blinkatest.py
Hello blinka!
Digital IO ok!
I2C ok!
SPI ok!
done!
```

Also, to make sure the wiring is good, we are going to use `sudo i2cdetect -y 1` to see if our devices are detected:
```sh
pi@planktoscope:~ $ sudo i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- 0d -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: 60 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: 70 -- -- -- -- -- -- --
```

The device appearing at addresses 60 and 70 is our motor controller. Address `0d` is the fan controller and `3c` is the oled screen (we'll set up both a bit further down). Your version of the RGB Cooling Hat may not have the screen, it's fine as the screen is not necessary for proper operation of the Planktoscope.

In case the motor controller does not appear, shutdown your Planktoscope and check the wiring. If your board is using a connector instead of a soldered pin connection (as happens with the Adafruit Bonnet Motor Controller), sometimes the pins on the male side need to be bent a little to make good contact. In any case, do not hesitate to ask for help in Slack.

### [PSCOPE_HAT VERSION] Test the stepper controllers
After wiring the steppers, please run the following script, you can create it in `~/test/stepper_controller.py`:
```python
#!/usr/bin/python3
import shush
import time

m1 = shush.Motor(0)
m1.enable_motor()
m2 = shush.Motor(1)
m2.enable_motor()


# This function takes the target position as an input.
# It prints the current position and the iteration.
# The motor spins until it gets to the target position
# before allowing the next command.
def spin(motor, target):
    motor.go_to(target)

    i = 0

    while motor.get_position() != target:
        print(motor.get_position())
        print(i)
        i += 1


while True:
    # Spin 5 rotations from start
    spin(m1, 256000)

    time.sleep(0.5)
    # Spin back 5 rotations to starting point
    spin(m1, 0)

    time.sleep(0.5)
    # Spin 5 rotations from start
    spin(m2, 256000)

    time.sleep(0.5)
    # Spin back 5 rotations to starting point
    spin(m2, 0)

    time.sleep(0.5)
```

To start the script, just run the following:
```sh
chmod +x ~/test/stepper_controller.py
~/test/stepper_controller.py
```

The pump should run in one direction then in the other, and the focus stage should move in one direction and then in another.

### Deactivate steppers
Create `sudo nano /etc/systemd/system/gpio-init.service`:
```
[Unit]
Description=GPIO Init
DefaultDependencies=false

[Service]
Type=oneshot
ExecStart=/usr/bin/stepper-disable
Restart=no

[Install]
WantedBy=sysinit.target
```

And activate with `sudo systemctl enable autohotspot.service`.


Create the script with `sudo nano /usr/bin/stepper-disable`:
```sh
#!/bin/sh -e


# Initialise GPIO 4 and 12 to output to deactivate the steppers
if [ ! -e /sys/class/gpio/gpio4 ]; then
    echo "4" > /sys/class/gpio/export
fi

if [ ! -e /sys/class/gpio/gpio12 ]; then
    echo "12" > /sys/class/gpio/export
fi
echo "out" > /sys/class/gpio/gpio4/direction
echo "out" > /sys/class/gpio/gpio12/direction
echo "1" > /sys/class/gpio/gpio4/value
echo "1" > /sys/class/gpio/gpio12/value
```

### Install Ultimate GPS HAT

You can start by testing that the GPS module is working. Either install your PlanktoScope with a view of the sky, or connect the external antenna.

Now you need to run the following:
```sh
sudo apt install gpsd gpsd-clients
stty -F /dev/serial0 raw 9600 cs8 clocal -cstopb
cat /dev/serial0
```

If the GPS works, you should now see NMEA sentences scrolling:
```
$GPGGA,000908.799,,,,,0,00,,,M,,M,,*7E
$GPGSA,A,1,,,,,,,,,,,,,,,*1E
$GPGSV,1,1,00*79
$GPRMC,000908.799,V,,,,,0.00,0.00,060180,,,N*44
$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32
$GPGGA,000909.799,,,,,0,00,,,M,,M,,*7F
$GPGSA,A,1,,,,,,,,,,,,,,,*1E
$GPRMC,000909.799,V,,,,,0.00,0.00,060180,,,N*45
$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32
$GPGGA,000910.799,,,,,0,00,,,M,,M,,*77
$GPGSA,A,1,,,,,,,,,,,,,,,*1E
$GPRMC,000910.799,V,,,,,0.00,0.00,060180,,,N*4D
$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32
```

Until you get a GPS fix, most of the sentences are empty (see the lines starting with GPGSA and with lot of commas).

We are going to use gpsd to parse the GPS data. We need to set it up by editing `/etc/default/gpsd`. This file is source just before starting gpsd and allows to configure its working.
```sh
sudo nano /etc/default/gpsd
```

Change the `USB_AUTO` line to read `false`
```sh
USBAUTO="false"
```

Also change the `DEVICES` line to add the device we are going to use `/dev/serial0`:
```sh
DEVICES="/dev/serial0"
```

Finally, we want to add the parameter `-n -r` to `GPSD_OPTIONS`:
```sh
GPSD_OPTIONS="-n -r"
```

Save your work, and restart gpsd by running the following:
```sh
sudo systemctl restart gpsd.service
```

If you wait a bit, you can run `gpsmon` to check that your configuration is correct. You should get an output similar to this:
```
pi@planktoscope:~ $ gpsmon
/dev/serial0                  NMEA0183>
┌──────────────────────────────────────────────────────────────────────────────┐
│Time: 2020-07-21T11:09:26.000Z Lat:  45 33' 28.08539" Non:   1 03' 44.02019" W│
└───────────────────────────────── Cooked TPV ─────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────┐
│ GPGGA GPGSA GPRMC GPZDA GPGSV                                                │
└───────────────────────────────── Sentences ──────────────────────────────────┘
┌──────────────────┐┌────────────────────────────┐┌────────────────────────────┐
│Ch PRN  Az El S/N ││Time:      110926.000       ││Time:      110927.000       │
│ 0  27 351 78  49 ││Latitude:     4533.4809 N   ││Latitude:  4533.4809        │
│ 1  21  51 69  47 ││Longitude:   00103.7367 W   ││Longitude: 00103.7367       │
│ 2  16 184 61  43 ││Speed:     0.00             ││Altitude:  -0.1             │
│ 3  10 116 51  50 ││Course:    201.75           ││Quality:   2   Sats: 11     │
│ 4   8 299 47  49 ││Status:    A       FAA: D   ││HDOP:      0.87             │
│ 5  20  66 42  46 ││MagVar:                     ││Geoid:     49.3             │
│ 6 123 138 28  43 │└─────────── RMC ────────────┘└─────────── GGA ────────────┘
│ 7  26 165 25  30 │┌────────────────────────────┐┌────────────────────────────┐
│ 8  11 264 23  48 ││Mode: A3 ...s: 27 21 16 10  ││UTC:           RMS:         │
│ 9   7 303 15  38 ││DOP: H=0.87  V=1.13  P=1.42 ││MAJ:           MIN:         │
│10  18  56 14  44 ││TOFF:  0.530187817          ││ORI:           LAT:         │
│11  30 330  5  35 ││PPS:                        ││LON:           ALT:         │
└────── GSV ───────┘└──────── GSA + PPS ─────────┘└─────────── GST ────────────┘
(42) $GPGSV,4,4,14,15,03,035,36,01,02,238,*72
(72) $GPRMC,110922.000,A,4533.4809,N,00103.7366,W,0.01,322.19,210720,,,D*7E
(35) $GPZDA,110922.000,21,07,2020,,*5B
(81) $GPGGA,110923.000,4533.4809,N,00103.7367,W,2,11,0.87,-0.1,M,49.3,M,0000,0000*5B
(64) $GPGSA,A,3,16,27,30,10,18,21,20,08,11,07,26,,1.43,0.87,1.13*0B
(72) $GPRMC,110923.000,A,4533.4809,N,00103.7367,W,0.01,188.90,210720,,,D*7D
(35) $GPZDA,110923.000,21,07,2020,,*5A
(81) $GPGGA,110924.000,4533.4809,N,00103.7367,W,2,11,0.87,-0.1,M,49.3,M,0000,0000*5C
(64) $GPGSA,A,3,16,27,30,10,18,21,20,08,11,07,26,,1.43,0.87,1.13*0B
(72) $GPRMC,110924.000,A,4533.4809,N,00103.7367,W,0.01,156.23,210720,,,D*71
```

You can leave with `CTRL+C`.

#### Bonus Configuration: Automatic time update from GPSD

The Adafruit GPS HAT allows your PlanktoScope to automatically sets its time to the GPS received one. Moreover, since the PPS (Pulse Per Second) output is activated, you can even set your PlanktoScope to act as a stratum 1 timeserver.

We are first going to make sure that your PlanktoScope receives proper PPS signal. We need to add the following line at the end of `/boot/config.txt`:
```
sudo nano /boot/config.txt
# Add the following line at the end of the line
dtoverlay=pps-gpio,gpiopin=4
```

We also need to activate the pps module of the kernel, by editing `/etc/modules`:

```
sudo nano /etc/modules
# Add the following line at the end of the line
pps-gpio
```

Now install `pps-tools` so we can check that this is properly running.
```sh
sudo apt install pps-tools
```

Finally, in the `/etc/default/gpsd` file, we need to add our pps device to the line `DEVICES`. Append `/dev/pps0`:
```sh
DEVICES="/dev/serial0 /dev/pps0"
```

Reboot your PlanktoScope now and check that the PPS signal is properly parsed by the PlanktoScope. You can do this by running `sudo ppstest /dev/pps0`:
```
pi@planktoscope:~ $ sudo ppstest /dev/pps0
trying PPS source "/dev/pps0"
found PPS source "/dev/pps0"
ok, found 1 source(s), now start fetching data...
source 0 - assert 1595329939.946478786, sequence: 4125 - clear  0.000000000, sequence: 0
source 0 - assert 1595329940.946459463, sequence: 4126 - clear  0.000000000, sequence: 0
```

`gpsmon` should also show a PPS signal in the `GSA + PPS` box.

We now need to install the software that will act as timeserver, both locally and globally. Its name is Chrony. It's a more modern replacement for `ntp`, using the same underlying protocol. Let's go ahead and install it:
```sh
sudo apt install chrony
```

We need to edit the configuration of chrony, to activate both the GPS time synchronization and to allow clients to request time updates directly from our microscope.

Edit the file `/etc/chrony/chrony.conf` and replace its content with the following:
```
pool pool.ntp.org iburst maxsources 4

driftfile /var/lib/chrony/drift

# allow to make big changes to clock if difference with ref clock is more than 1 seconds
makestep 1 5

refclock SHM 0 refid NMEA offset 0.006
refclock SHM 1 pps refid NME+
refclock SOCK /var/run/chrony.sock delay 0.0 refid SOCK
# noselect poll 8 filter 1000
#refclock PPS /dev/pps0 precision 1e-7 noselect refid GPPS

allow all

rtcsync

logdir /var/log/chrony
log rtc refclocks
```

Before restarting `chrony`, we need to make sure the timesync service from systemd is deactivated:
```sh
sudo systemctl stop systemd-timesyncd.service
sudo systemctl disable systemd-timesyncd.service
```

Final step, let's start `chrony` with its new configuration and restart `gpsd`:
```sh
sudo systemctl restart chrony
sudo systemctl restart gpsd
```

To check that everything is working as intended, wait a few minutes, and then type `chronyc sources -v`. This command will show the time sources `chrony` is using, and right at the top there should be our NMEA source. Make sure its line starts with `#*`, which means this source is selected:
```
pi@planktoscope:~ $ chronyc sources -v
210 Number of sources = 5

  .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
 / .- Source state '*' = current synced, '+' = combined , '-' = not combined,
| /   '?' = unreachable, 'x' = time may be in error, '~' = time too variable.
||                                                 .- xxxx [ yyyy ] +/- zzzz
||      Reachability register (octal) -.           |  xxxx = adjusted offset,
||      Log2(Polling interval) --.      |          |  yyyy = measured offset,
||                                \     |          |  zzzz = estimated error.
||                                 |    |           \
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
#* NMEA                          0   4   377    13   -434ns[ -582ns] +/-  444ns
^- mail.raveland.org             3   7   377   215    -18ms[  -18ms] +/-   53ms
^- nio.nucli.net                 2   6   377    19  -7340us[-7340us] +/-   63ms
^- ntp4.kashra-server.com        2   8   377   146    -11ms[  -11ms] +/-   50ms
^- pob01.aplu.fr                 2   8   377    83    -15ms[  -15ms] +/-   66ms
```

The other servers are here just as fallback measures, in case the GPS is not working for an unknown reason.

This part is now complete! Everytime you start your Planktoscope, it will set its own time after a few minutes (once a GPS signal is acquired).

The ultimate step will have to be done on the other equipment on the network where you want to use this time source. You will need to add the line `server planktoscope.local` to your ntp configuration file either at `/etc/ntp.conf` or at `/etc/chrony/chrony.conf` and then restart your ntp service.

You can find more information in this hardware module in Adafruit documentation at [Installing Adafruit GPS HAT](https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi/overview) or on this page to [use Python Thread with GPS HAT](http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/)


### Install RGB Cooling HAT
To setup the RGB Cooling HAT, you just need to clone and build the WiringPi library:
```sh
cd ~/libraries
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
sudo ./build
gpio -v
```

The last command should output something similar to the following:
```
gpio version: 2.60
Copyright (c) 2012-2018 Gordon Henderson
This is free software with ABSOLUTELY NO WARRANTY.
For details type: gpio -warranty

Raspberry Pi Details:
  Type: Pi 4B, Revision: 01, Memory: 4096MB, Maker: Sony
  * Device tree is enabled.
  *--> Raspberry Pi 4 Model B Rev 1.1
  * This Raspberry Pi supports user-level GPIO access.

```

You will also need to install some python modules:
```sh
sudo apt install i2c-tools
sudo pip3 install smbus2
```

More information can be found on Yahboom website, on the page [Installing RGB Cooling HAT](https://www.yahboom.net/study/RGB_Cooling_HAT).


### Install Mosquitto MQTT

In order to send and receive data from Node-RED, you need to install this. Run the following:
```
sudo apt install mosquitto mosquitto-clients

```

### Check OpenCV's installation

We need to install the latest OpenCV version. Unfortunately, it is not available in the repositories. We are going to install it directly by using pip.

First, we need to install the needed dependencies, then we will directly install opencv:
```sh
sudo apt install libgtk-3-0 libavformat58 libavcodec58 libqt4-test libopenexr23 libilmbase23 libqtgui4 libavutil56 libjasper1 libqtcore4 libcairo-gobject2 libswscale5 libhdf5-dev libilmbase-dev libopenexr-dev libgstreamer1.0-dev libavcodec-dev libavformat-dev libswscale-dev libwebp-dev libatlas-base-dev
```

Install now openCV diretly with pip:
```sh
pip install opencv-contrib-python
```

You can now check that opencv is properly installed by running a python interpreter and importing the cv2 module.
```sh
pi@planktoscope:~ $ python3
Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'4.4.0'
>>> quit()
```

If all goes well, the displayed version number should be `4.4.0`.

More detailed information can be found on this [website](https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/).


### Check MorphoCut's installation

To test the installation, open up once again a python interpreter and import the morphocut module:
```sh
pi@planktoscope:~ $ python3
Python 3.7.3 (default, Dec 20 2019, 18:57:59)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import morphocut
>>> morphocut.__version__
'0.1.1+42.g01a051e'
>>> quit()
```

The MorphoCut documentation can be found [on this page](https://morphocut.readthedocs.io/en/stable/index.html).


### Nginx Setup

To display the gallery, we need to setup an nginx webserver.

Type in the following commands:
```
sudo apt install nginx
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /home/pi/PlanktoScope/scripts/gallery/gallery.conf /etc/nginx/sites-enabled/gallery.conf
sudo nginx -t && sudo systemctl reload nginx
```

If you navigate to http://planktoscope.local:80, you should see the library opened.

### Install Node-RED

#### Download and installation
To install Node.js, npm and Node-RED onto a Raspberry Pi, you just need to run the following command. You can review the content of this script [here](https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered).
```sh
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
Type `y` at both prompts to accept the installation and its settings.

### Override Node-RED default settings to make it start after Mosquitto

We need to make sure nodered only starts after Mosquitto. And Mosquitto waits for a network connection to appear before starting.

To change this behavior, we need to override Node-red default setting. We modify the default service unit file with the following:
```sh
sudo mkdir -p /etc/systemd/system/nodered.service.d/
sudo cp /home/pi/PlanktoScope/scripts/raspbian_configuration/etc/systemd/system/nodered.service.d/override.conf /etc/systemd/system/nodered.service.d/override.conf
sudo systemctl daemon-reload
```

#### Enable start on boot and launch Node-RED
To run Node-RED when the Pi is turned on or restarted, you need to enable the systemd service by running this command:
```sh
sudo systemctl enable nodered.service
```

You can now start Node-RED by running the following:
```sh
sudo systemctl start nodered.service
```

#### Check the installation
Make sure Node-RED is correctly installed by reaching the following page from the browser of your pi http://localhost:1880 or http://planktoscope.local:1880 from another computer on the same network.

#### Install the necessary nodes and activate necessary features

We are going to activate the Projects feature of Node-Red as this will help us manage and track changes to the flows. Open the file `settings.js` with an editor (for example with `nano ~/.node-red/settings.js`) so we can change the following lines (you can use `CTRL+_` to quickly navigate to the line indicated):

 - Line 75: uncomment the line (remove the //) that ends with flowFilePretty: true,
 - Line 337: set enabled to true

Restart Node-RED to take into account those changes:
```sh
sudo systemctl restart nodered.service
```

We need to move the PlanktoScope folder in the right place, in the `projects` subfolder of Node-Red and link this new folder to our `/home/`. To do so, in the terminal type the following::
```sh
mv /home/pi/PlanktoScope /home/pi/.node-red/projects/
ln -s ./.node-red/projects/PlanktoScope /home/pi/PlanktoScope
```

We will now install the missing nodes. These nodes will be used by the PlanktoScope software:
```sh
cd /home/pi/.node-red/
npm install copy-dependencies
node_modules/copy-dependencies/index.js projects/PlanktoScope ./
npm update
```

Save you changes.

The final step before restarting node-red is to link the projects directory from within node-red folder to our main home directory. To do so, just open a terminal and type the following:

You can now restart the nodered service:
```
sudo systemctl restart nodered.service
```

#### Import the last GUI

If you now open the Node-Red GUI in your browser, it will ask you to setup the project, an email and a username (so if you make changes to the flow and want to share them we can know who made them).

Open your browser and navigate to http://planktoscope.local:1880. In the prompt, select `Open existing project` button at the bottom, choose the PlanktoScope project and click on `Open Project`. Eventually, merge the proposed changes.

The latest flow version will be available immediately.


#### More information
[Installing Node-RED on Raspberry Pi](https://nodered.org/docs/getting-started/raspberrypi)


## Finishing the install

Make sure to update your Pi
```
sudo apt update -y
sudo apt full-upgrade -y
```

Reboot your Pi safely
```
sudo reboot now

```

## Useful later maybe

### Update the cloned repository

Updates are published on Github regurlarly. Make sure to update once in a while by running this command:
```sh
cd PlanktoScope
git pull
```

This will pull and merge all the changes made since your last update.

### Share WiFi via Ethernet

At this link : https://www.instructables.com/id/Share-WiFi-With-Ethernet-Port-on-a-Raspberry-Pi/



