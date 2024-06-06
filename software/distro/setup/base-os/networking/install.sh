#!/bin/bash -eux
# The networking configuration enables access to network services via static IP over Ethernet, and
# via self-hosted wireless AP when a specified external wifi network is not available.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install dependencies
sudo apt-get install -y -o Dpkg::Progress-Fancy=0 \
  firewalld dnsmasq hostapd avahi-utils

# By default hostapd.service is masked and enabled (which causes two symlinks to exist), which
# prevents Forklift from being able to disable hostapd via a filesystem overlay. We override this by
# manually removing those symlinks by default, since our autohotspot relies on hostapd being
# unmaske and disabled.
sudo systemctl unmask hostapd.service
sudo systemctl disable hostapd.service

# Disable firewalld for now
# FIXME: enable firewalld and set up firewall rules
if sudo systemctl disable firewalld.service --now 2>/dev/null; then
  if systemctl list-units --full -all | grep -Fq "docker.service"; then
    # Restart docker to integrate with firewalld
    sudo systemctl restart docker
  fi
else
  # We can't stop it because we're not booted, so we don't need to stop it or restart Docker:
  sudo systemctl disable firewalld.service
fi
