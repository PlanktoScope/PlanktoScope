#!/bin/bash -eux

# Note: in general, 0 represents "success/yes/selected", while 1 represents "failed/no/unselected",
# but there is no consistent meaning. Partial documentation of raspi-commands is available at
# https://www.raspberrypi.com/documentation/computers/configuration.html, but the authoritative
# reference for commands and their parameters is at
# https://github.com/RPi-Distro/raspi-config/blob/master/raspi-config . It is discouraged to use
# raspi-config commands when a reasonable platform-independent alternative exists, because they make
# it harder for our project to enable running the PlanktoScope software on computers besides the
# Raspberry Pi. So we should avoid adding more raspi-config commands.

if ! command -v raspi-config &>/dev/null; then
  echo "Warning: raspi-config is unavailable, so no RPi-specific hardware configuration will be applied!"
  exit 0
fi

# The following commands enable the SPI and I2C hardware interfaces:
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

# The following command enables the serial port and serial port console.
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_serial_cons 0

# The following command disables legacy camera support so that we can use libcamera:
sudo raspi-config nonint do_legacy 1
