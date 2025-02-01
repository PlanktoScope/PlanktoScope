#!/bin/bash -eux
# The networking configuration enables access to network services via static IP over Ethernet, and
# via self-hosted wireless AP when a specified external wifi network is not available.

# Determine the base path for copied files
config_files_root=$(dirname "$(realpath "$BASH_SOURCE")")

# Install dependencies
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  network-manager firewalld dnsmasq-base hostapd avahi-utils
sudo systemctl enable NetworkManager.service

# Uninstall dhcpcd if we're on bullseye
DISTRO_VERSION_ID="$(. /etc/os-release && echo "$VERSION_ID")"
if [ "$DISTRO_VERSION_ID" -le 11 ]; then # Support Raspberry Pi OS 11 (bullseye)
  sudo -E apt-get purge -y -o Dpkg::Progress-Fancy=0 \
    dhcpcd5
fi

# By default hostapd.service is masked and enabled (which causes two symlinks to exist), which
# prevents Forklift from being able to disable hostapd via a filesystem overlay. We override this by
# manually removing those symlinks by default, since our autohotspot relies on hostapd being
# unmasked and disabled.
sudo systemctl unmask hostapd.service
sudo systemctl disable hostapd.service

# Set the wifi country
# FIXME: instead have the user set the wifi country via a first-launch setup wizard, and do it
# without using raspi-config. It should also be updated if the user changes the wifi country.
# This should also update the hostapd config (maybe via a new template variable)
if command -v raspi-config &>/dev/null; then
  sudo raspi-config nonint do_wifi_country US
else
  echo "Warning: raspi-config is not available, so we can't set the wifi country!"
fi
