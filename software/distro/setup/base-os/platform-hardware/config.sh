#!/bin/bash -eux
# The platform hardware configuration is for configuration specific to the underlying compute
# platform used to run the operating system. Currently the only supported platform hardware is the
# Raspberry Pi 4. Hopefully, in the future other platforms will also be supported - in which case
# alternative OS build scripts will be needed for configuration.

# Note: in general, 0 represents "success/yes/selected", while 1 represents "failed/no/unselected",
# but there is no consistent meaning. Partial documentation of raspi-commands is available at
# https://www.raspberrypi.com/documentation/computers/configuration.html, but the authoritative
# reference for commands and their parameters is at
# https://github.com/RPi-Distro/raspi-config/blob/master/raspi-config . It is discouraged to use
# raspi-config commands when a reasonable platform-independent alternative exists, because they make
# it harder for our project to enable running the PlanktoScope software on computers besides the
# Raspberry Pi. So we should avoid adding more raspi-config commands.

# The following commands enable the SPI and I2C hardware interfaces:
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

# The following command enables the serial port and serial port console.
# do_serial_cons and do_serial_hw are needed for Raspberry Pi OS 12 (bookworm) and above, while
# do_serial is needed for Raspberry Pi OS (bullseye).
sudo raspi-config do_serial_hw 0 || sudo raspi-config nonint do_serial 0
sudo raspi-config do_serial_cons 0 || sudo raspi-config nonint do_serial 0

# The following command enables the camera on the 32-bit Raspberry Pi OS (ARMv7):
sudo raspi-config nonint do_camera 0
# The following command enables legacy camera support on the 64-bit Raspberry Pi OS (ARM64):
sudo raspi-config nonint do_legacy 0

# The following command sets the GPU memory to 256:
sudo raspi-config nonint do_memory_split 256
