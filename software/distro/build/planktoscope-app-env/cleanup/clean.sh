#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Clean up any unnecessary apt files
sudo apt-get autoremove -y
sudo apt-get clean -y

# Clean up any unnecessary pip & npm files
pip3 cache purge

# Remove SSH keys and make them be regenerated
sudo rm -f /etc/ssh/ssh_host_*
sudo systemctl enable regenerate_ssh_host_keys.service

# Remove history files
rm -f /home/pi/.bash_history
rm -f /home/pi/.python_history
