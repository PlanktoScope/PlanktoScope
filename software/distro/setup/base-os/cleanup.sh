#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Remove unnecessary packages:
sudo apt-get remove -y gcc
sudo apt-get remove -y gcc-10 || true
sudo apt-get remove -y gcc-12 || true

# Clean up any unnecessary apt files:
sudo apt-get autoremove -y
sudo apt-get clean -y

# Clear machine-id so that it will be regenerated on the next boot
# (refer to https://www.freedesktop.org/software/systemd/man/latest/machine-id.html):
sudo bash -c 'printf "" > /var/lib/dbus/machine-id'
sudo bash -c 'printf "uninitialized\n" > /etc/machine-id'

# Clear other secrets (refer to https://systemd.io/BUILDING_IMAGES/):
sudo rm -f /var/lib/systemd/random-seed
sudo rm -f /var/lib/systemd/credential.secret

# Remove SSH keys:
sudo rm -f /etc/ssh/ssh_host_*_key*
