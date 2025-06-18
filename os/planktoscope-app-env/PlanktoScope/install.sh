#!/bin/bash -eux

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
distro_setup_files_root="$(dirname "$(dirname "$config_files_root")")"
repo_root="$(dirname "$distro_setup_files_root")"

# The PlanktoScope monorepo is used for running and iterating on software components
# https://github.com/PlanktoScope/planktoscope
sudo cp -r "$repo_root" "$HOME/PlanktoScope"
sudo chown -R pi:pi "$HOME/PlanktoScope"

# Configure firmware
# https://www.raspberrypi.com/documentation/computers/config_txt.html
sudo bash -c "cat \"$config_files_root/config.txt.snippet\" >> \"/boot/firmware/config.txt\""

# Disable the 4 Raspberry logo in the top left corner
# more space for kernel and system logs
sudo sed -i -e 's/$/ logo.nologo/' /boot/firmware/cmdline.txt

# Create a file needed by the "set country" Node-RED node
sudo cp -r "$config_files_root/cfg80211_regdomain.conf" "/etc/modprobe.d/"
sudo chown -R pi:pi "/etc/modprobe.d/cfg80211_regdomain.conf"
