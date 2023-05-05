#!/bin/bash -eux
# The networking configuration enables access to network services via static IP over Ethernet, and
# via self-hosted wireless AP when a specified external wifi network is not available.

config_files_root=$(dirname $(realpath $0))

# Install dependencies
sudo apt-get update -y
sudo apt-get install -y ufw dnsmasq hostapd

# Force reinitialization of the machine ID
sudo bash -c "echo \"uninitialized\" > /etc/machine-id"

# Set the wifi country
# FIXME: instead have the user set the wifi country via a first-launch setup wizard, and do it
# without using raspi-config. It should also be updated if the user changes the wifi country.
sudo raspi-config nonint do_wifi_country us
sudo rfkill unblock wifi

# FIXME: set up the SSH server without using raspi-config
sudo raspi-config nonint do_ssh 0

# TODO: add basic ufw settings

# Change hostapd settings
sudo systemctl unmask hostapd
sudo systemctl disable dnsmasq
sudo systemctl disable hostapd
# FIXME: the config file sets a country code which needs to be updated for local countries (and
# should be updated if the user changes the wifi country), and a channel which may need to be changed
# by the user in crowded wireless network environments
file="/etc/hostapd/hostapd.conf"
sudo cp "$config_files_root$file" "$file"

# TODO: make a proper systemd unit and script to update the SSID field of hostapd.conf and the system hostname, instead of putting a Python snippet in /etc/rc.local

# Change dnsmasq settings
file="/etc/dnsmasq.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""

# Change dhcpcd settings
file="/etc/dhcpcd.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""
file="/etc/dhcpcd.enter-hook"
sudo cp "$config_files_root$file" "$file"

# Set up autohotspot service
file="/etc/systemd/system/autohotspot.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable autohotspot.service
file="/etc/systemd/system/autohotspot.timer"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable autohotspot.timer
file="/home/pi/.local/bin/autohotspot"
cp "$config_files_root$file" "$file"
