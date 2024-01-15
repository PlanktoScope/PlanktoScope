#!/bin/bash -eux
# The networking configuration sets PlanktoScope-specific network settings.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install dependencies
sudo apt-get install -y avahi-utils

# Set the default hostname, which will be updated with the machine name on boot
current_hostname=$(hostnamectl status --static)
new_hostname="pkscope"
sudo bash -c "echo \"$new_hostname\" > /etc/hostname"
sudo sed -i "s/^127\.0\.1\.1.*$current_hostname$/127.0.1.1\t$new_hostname/g" /etc/hosts
sudo hostnamectl set-hostname "$new_hostname"

# Set the default SSID for the self-hosted wifi network, which will be updated with the machine name on boot
file="/etc/hostapd/hostapd-ssid-autogen-warning.snippet"
# This sed command uses `~` instead of `/` because the warning comments also include `/` characters.
# The awk subcommand is needed to escape newlines for sed.
sudo sed -i "s~^ssid=.*$~$(awk '{printf "%s\\n", $0}' $file)ssid=pkscope~g" /etc/hostapd/hostapd.conf

# Download tool to generate machine names based on serial numbers
mkdir -p $HOME/.local/bin/machine-name
machinename_version="0.1.3"
curl -L "https://github.com/PlanktoScope/machine-name/releases/download/v$machinename_version/machine-name_${machinename_version}_linux_arm.tar.gz" \
  | sudo tar -xz -C /usr/bin/ machine-name
sudo mv /usr/bin/machine-name "/usr/bin/machine-name-${machinename_version}"
sudo ln -s "/usr/bin/machine-name-${machinename_version}" /usr/bin/machine-name

# Automatically generate the machine name and write it to a file upon boot
mkdir -p $HOME/.local/etc
file="$HOME/.local/etc/machine-name"
cp "$config_files_root$file" "$file"
file="/etc/systemd/system/planktoscope-org.update-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-machine-name.service

# Automatically update the SSID upon creation of the self-hosted wifi network based on the machine name
mkdir -p $HOME/.local/etc/hostapd
file="$HOME/.local/etc/hostapd/ssid.snippet"
cp "$config_files_root$file" "$file"
file="/etc/systemd/system/planktoscope-org.update-ssid-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-ssid-machine-name.service

# Change Cockpit settings
file="/etc/cockpit/cockpit.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""

# Automatically update the Cockpit origins upon boot with the machine name
mkdir -p $HOME/.local/etc/cockpit
file="/etc/systemd/system/planktoscope-org.update-cockpit-origins-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-cockpit-origins-machine-name.service

# Change dnsmasq settings
file="/etc/dnsmasq.d/planktoscope.conf"
sudo cp "$config_files_root$file" "$file"
mkdir -p $HOME/.local/etc
file="$HOME/.local/etc/hosts-autogen-warning.snippet"
cp "$config_files_root$file" "$file"
file="$HOME/.local/etc/hosts-base.snippet"
cp "$config_files_root$file" "$file"
cp "$HOME/.local/etc/hosts-autogen-warning.snippet" \
  "$HOME/.local/etc/hosts"
cat "$HOME/.local/etc/hosts-base.snippet" \
  >> "$HOME/.local/etc/hosts"

# Automatically update hostnames upon boot with the machine name
mkdir -p $HOME/.local/etc
file="/etc/systemd/system/planktoscope-org.update-hosts-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-hosts-machine-name.service
file="/etc/systemd/system/planktoscope-org.update-hostname-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-hostname-machine-name.service

# Publish planktoscope.local and pkscope.local mDNS aliases
file="/etc/systemd/system/planktoscope-org.avahi-alias-planktoscope.local.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.avahi-alias-planktoscope.local.service
file="/etc/systemd/system/planktoscope-org.avahi-alias-pkscope.local.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.avahi-alias-pkscope.local.service
