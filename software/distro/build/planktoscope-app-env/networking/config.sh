#!/bin/bash -eux
# The networking configuration sets PlanktoScope-specific network settings.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Set the default hostname, which will be overwritten with the device-specific MAC-address-based ID
# on each boot
current_hostname=$(hostnamectl status --static)
new_hostname="planktoscope"
sudo bash -c "echo \"$new_hostname\" > /etc/hostname"
sudo sed -i "s/127\.0\.1\.1.*${current_hostname}/127.0.1.1\t${new_hostname}/g" /etc/hosts

# Set the default SSID for the self-hosted wifi network
sudo sed -i "s/^ssid=.*$/ssid=PlanktoScope/g" /etc/hostapd/hostapd.conf

# Download tool to generate machine names based on serial numbers
curl -L https://github.com/PlanktoScope/machine-name/releases/download/v0.1.0/machine-name_0.1.0_linux.arm.tar.gz \
  | tar -xz -C /home/pi/.local/bin/ machine-name

# Automatically update the SSID upon creation of the self-hosted wifi network based on the RPi's serial number
mkdir -p /home/pi/.local/bin
file="/home/pi/.local/bin/update-ssid-machine-name.sh"
cp "$config_files_root$file" "$file"
file="/etc/systemd/system/planktoscope-org.update-ssid-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-ssid-machine-name.service

# Change dnsmasq settings
file="/etc/dnsmasq.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""
mkdir -p /home/pi/.local/etc
file="/home/pi/.local/etc/hosts"
cp "$config_files_root$file" "$file"

# Automatically update hostnames upon boot based on the RPi's serial number
file="/home/pi/.local/etc/hosts-base.snippet"
cp "$config_files_root$file" "$file"
file="/home/pi/.local/etc/hosts-machine-name.snippet"
cp "$config_files_root$file" "$file"
file="/home/pi/.local/bin/update-hosts-machine-name.sh"
cp "$config_files_root$file" "$file"
file="/etc/systemd/system/planktoscope-org.update-hosts-machine-name.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.update-hosts-machine-name.service
