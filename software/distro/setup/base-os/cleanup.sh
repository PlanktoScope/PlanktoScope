#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Clean up any unnecessary apt files
sudo apt-get autoremove -y
sudo apt-get clean -y

# Clear machine-id so that it will be regenerated on the next boot
sudo bash -c 'printf "" > /var/lib/dbus/machine-id'
sudo bash -c 'printf "uninitialized" > /etc/machine-id'

# Remove SSH keys so that they'll be regenerated on the next boot
sudo rm -f /etc/ssh/ssh_host_*
#sudo systemctl enable regenerate_ssh_host_keys.service
