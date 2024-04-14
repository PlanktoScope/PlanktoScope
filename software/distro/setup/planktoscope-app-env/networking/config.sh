#!/bin/bash -eux
# The networking configuration sets PlanktoScope-specific network settings.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install dependencies
sudo apt-get install -y avahi-utils

# Download tool to generate machine names based on serial numbers
machinename_version="0.1.3"
arch="$(dpkg --print-architecture | sed -e 's/armhf/arm/' -e 's/aarch64/arm64/')"
curl -L "https://github.com/PlanktoScope/machine-name/releases/download/v$machinename_version/machine-name_${machinename_version}_linux_${arch}.tar.gz" \
  | sudo tar -xz -C /usr/bin/ machine-name
sudo mv /usr/bin/machine-name "/usr/bin/machine-name-${machinename_version}"
sudo ln -s "machine-name-${machinename_version}" /usr/bin/machine-name

# Set the default hostname, which will be updated with the machine name on boot
# TODO: provide this functionality from pallet-standard instead?
current_hostname=$(hostnamectl status --static)
new_hostname="pkscope"
sudo hostnamectl hostname "$new_hostname"
sudo sed -i "s/^127\.0\.1\.1.*$current_hostname$/127.0.1.1\t$new_hostname/g" /etc/hosts

# TODO: remove this by updating the Node-RED frontend and Python backend:
# Add a symlink at /var/lib/planktoscope/machine-name for compatibility with the Node-RED frontend
# and Python backend, which are not yet updated to check /run/machine-name instead:
sudo ln -s /run/machine-name /var/lib/planktoscope/machine-name

# TODO: provide this functionality from pallet-standard instead:
# Automatically update the SSID upon creation of the self-hosted wifi network based on the machine name
file="$config_files_root/etc/hostapd/hostapd-ssid-autogen-warning.snippet"
# This sed command uses `~` instead of `/` because the warning comments also include `/` characters.
# The awk subcommand is needed to escape newlines for sed.
sudo sed -i "s~^ssid=\(.*\)$~$(awk '{printf "%s\\n", $0}' $file)ssid=\\1~g" /etc/hostapd/hostapd.conf
file="/etc/systemd/system/planktoscope-org.update-hostapd-ssid-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-hostapd-ssid-machine-name.service

# TODO: provide this functionality from pallet-standard instead:
# Change Cockpit settings
file="/etc/cockpit/cockpit.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""

# TODO: provide this functionality from pallet-standard instead:
# Automatically update the Cockpit origins upon boot with the machine name
file="/etc/systemd/system/planktoscope-org.update-cockpit-origins-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-cockpit-origins-machine-name.service

# TODO: provide this functionality from pallet-standard instead:
# Change dnsmasq settings
file="/etc/dnsmasq.d/planktoscope.conf"
sudo cp "$config_files_root$file" "$file"
file="/etc/systemd/system/planktoscope-org.update-hosts-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-hosts-machine-name.service

# TODO: provide this functionality from pallet-standard instead:
# Automatically update system hostname upon boot with the machine name
file="/etc/systemd/system/planktoscope-org.update-hostname-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-hostname-machine-name.service

# TODO: provide this functionality from pallet-standard instead:
# Publish planktoscope.local and pkscope.local mDNS aliases
file="/etc/systemd/system/planktoscope-org.avahi-alias-planktoscope.local.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.avahi-alias-planktoscope.local.service
file="/etc/systemd/system/planktoscope-org.avahi-alias-pkscope.local.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.avahi-alias-pkscope.local.service
