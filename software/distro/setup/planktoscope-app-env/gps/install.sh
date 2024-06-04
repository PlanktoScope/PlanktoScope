#!/bin/bash -eux
# The GPS driver provides support for a GPS device over serial, as well as system clock updating
# from GPS.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install dependencies
sudo apt-get install -y -o Dpkg::Progress-Fancy=0 \
  gpsd pps-tools chrony

# The following command enables the serial port but disables the login shell over the serial port.
# We use this because the serial port is reserved for a GPS device.
# Note that this overrides a setting in the base-os/platform-hardware/config.sh script.
DISTRO_VERSION_ID="$(. /etc/os-release && echo "$VERSION_ID")"
if [ $DISTRO_VERSION_ID -ge 12 ]; then # Support Raspberry Pi OS 12 (bookworm)
  sudo raspi-config nonint do_serial_cons 1
else # Support Raspberry Pi OS 11 (bullseye)
  sudo raspi-config nonint do_serial 2
fi

# Enable automatic time update from GPSD
file="/boot/config.txt"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""

# Use chrony instead of systemd-timesyncd (but do we really actually want to do this??):
if ! sudo systemctl disable systemd-timesyncd.service --now; then
  # If we're in an unbooted container, the service isn't running - so we don't need to stop it now:
  sudo systemctl disable systemd-timesyncd.servkce
fi
