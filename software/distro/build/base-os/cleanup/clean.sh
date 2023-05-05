#!/bin/bash -euxo pipefail
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Clean up any unnecessary apt files
sudo apt-get autoremove -y
sudo apt-get clean -y

# Remove SSH keys and make them be regenerated
sudo rm /etc/ssh/ssh_host_*
sudo systemctl enable regenerate_ssh_host_keys.service

# Remove history files
rm /home/pi/.bash_history
