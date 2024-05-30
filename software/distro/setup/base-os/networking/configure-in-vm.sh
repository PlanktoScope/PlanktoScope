#!/bin/bash -eux

# Set the wifi country
# FIXME: instead have the user set the wifi country via a first-launch setup wizard, and do it
# without using raspi-config. It should also be updated if the user changes the wifi country.
# This should also update the hostapd config (maybe via a new template variable)
if command -v raspi-config &> /dev/null; then
  sudo raspi-config nonint do_wifi_country US
  sudo rfkill unblock wifi
else
  echo "Warning: raspi-config is not available, so we can't set the wifi country!"
fi
