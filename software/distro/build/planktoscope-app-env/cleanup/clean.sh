#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Clean up any unnecessary apt files
sudo apt-get autoremove -y
sudo apt-get clean -y

# Clean up any unnecessary pip & npm files
pip3 cache purge || true
POETRY_VENV=/home/pi/.local/share/pypoetry/venv
$POETRY_VENV/bin/pip cache purge || true

# Remove SSH keys and make them be regenerated
sudo rm -f /etc/ssh/ssh_host_*
sudo systemctl enable regenerate_ssh_host_keys.service

# Remove history files
rm -f /home/pi/.bash_history
history -c && history -w
rm -f /home/pi/.python_history

# Delete images from the documentation directory, since they're huge and we aren't using them anyways
rm -rf /home/pi/PlanktoScope/documentation/
