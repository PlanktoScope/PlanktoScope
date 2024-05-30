#!/bin/bash -eux
# The networking configuration enables access to network services via static IP over Ethernet, and
# via self-hosted wireless AP when a specified external wifi network is not available.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install dependencies
sudo apt-get install -y firewalld dnsmasq hostapd avahi-utils

# By default hostapd.service is masked and enabled (which causes two symlinks to exist), which
# prevents Forklift from being able to disable hostapd via a filesystem overlay. We override this by
# manually removing those symlinks by default, since our autohotspot relies on hostapd being
# unmaske and disabled.
sudo systemctl unmask hostapd.service
sudo systemctl disable hostapd.service

# Set the wifi country
# FIXME: instead have the user set the wifi country via a first-launch setup wizard, and do it
# without using raspi-config. It should also be updated if the user changes the wifi country.
# This should also update the hostapd config (maybe via a new template variable)
if command -v raspi-config &> /dev/null; then
  sudo raspi-config nonint do_wifi_country US
else
  echo "Warning: raspi-config is not available, so we can't set the wifi country!"
fi

# Disable firewalld for now
# FIXME: enable firewalld and set up firewall rules
sudo systemctl disable firewalld.service --now

# Restart docker to integrate with firewalld
sudo systemctl restart docker
