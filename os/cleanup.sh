#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Remove unnecessary packages:
sudo apt purge -y gcc g++ gcc-12 triggerhappy

# Clean up any unnecessary apt files:
sudo apt autoremove -y
sudo apt clean -y

# Clear machine-id so that it will be regenerated on the next boot
# (refer to https://www.freedesktop.org/software/systemd/man/latest/machine-id.html):
sudo bash -c 'printf "" > /var/lib/dbus/machine-id'
sudo bash -c 'printf "uninitialized\n" > /etc/machine-id'

# Clear other secrets (refer to https://systemd.io/BUILDING_IMAGES/):
sudo rm -f /var/lib/systemd/random-seed
sudo rm -f /var/lib/systemd/credential.secret

# Remove SSH keys:
sudo rm -f /etc/ssh/ssh_host_*_key*

# Clean up any unnecessary pip, poetry, and npm files
poetry cache clear --no-interaction --all .
npm cache clean --force
rm -rf "$HOME"/.cache
mkdir "$HOME"/.cache

# Remove history files
rm -f "$HOME"/.python_history
rm -f "$HOME"/.bash_history
