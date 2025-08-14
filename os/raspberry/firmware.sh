#!/bin/bash -eux

# Configure firmware
# https://www.raspberrypi.com/documentation/computers/config_txt.html
sudo bash -c "cat \"config.ini\" >> \"/boot/firmware/config.txt\""

# Disable the 4 Raspberry logo in the top left corner
# more space for kernel and system logs
sudo sed -i -e 's/$/ logo.nologo/' /boot/firmware/cmdline.txt
