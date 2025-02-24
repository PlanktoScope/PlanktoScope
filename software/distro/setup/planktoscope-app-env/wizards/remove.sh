#!/bin/bash -eux

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# Disable the first-boot graphical wizard
if [ -f /etc/xdg/autostart/piwiz.desktop ]; then
  sudo mv /etc/xdg/autostart/piwiz.desktop /etc/xdg/autostart/piwiz.desktop.disabled
  file="/etc/lightdm/lightdm.conf"
  sudo cp "$config_files_root$file" "$file"
fi
