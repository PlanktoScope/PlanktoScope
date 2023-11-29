#!/bin/bash -eux
# The networking configuration enables access to network services via static IP over Ethernet, and
# via self-hosted wireless AP when a specified external wifi network is not available.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install dependencies
sudo apt-get update -y
sudo apt-get install -y ufw dnsmasq hostapd

# Force reinitialization of the machine ID
sudo bash -c "echo \"uninitialized\" > /etc/machine-id"

# Set the wifi country
# FIXME: instead have the user set the wifi country via a first-launch setup wizard, and do it
# without using raspi-config. It should also be updated if the user changes the wifi country.
sudo raspi-config nonint do_wifi_country US
sudo rfkill unblock wifi

# Set up ssh with host keys unique to each machine
# FIXME: set up the SSH server without using raspi-config
sudo raspi-config nonint do_ssh 0
sudo rm -f /etc/ssh/ssh_host_*
sudo systemctl enable regenerate_ssh_host_keys.service

# TODO: add basic ufw settings

# Change hostapd settings
# FIXME: the config file sets a country code which needs to be updated for local countries (and
# should be updated if the user changes the wifi country), and a channel which may need to be changed
# by the user in crowded wireless network environments
file="/etc/hostapd/hostapd.conf"
sudo cp "$config_files_root$file" "$file"
sudo systemctl unmask hostapd
sudo systemctl disable hostapd

# TODO: make a proper systemd unit and script to update the SSID field of hostapd.conf, instead of
# putting a Python snippet in /etc/rc.local
# Note that if we changed the system hostname then it'd also automatically change the mDNS hostname,
# which would be undesirable - it'd be difficult for us to help users if we can't tell them to just
# try connecting to "planktoscope.local" (works for devices with mDNS) or "plankto.scope" (works for
# devices which don't override DNS server settings).

# Change dnsmasq settings
file="/etc/dnsmasq.d/dhcp-and-dns.conf"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable dnsmasq # we'll always run dnsmasq as a DNS & DHCP server

# Change dhcpcd settings
file="/etc/dhcpcd.conf"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""

# Set up interface forwarding
file="/etc/sysctl.d/routed-ap.conf"
sudo cp "$config_files_root$file" "$file"
mkdir -p $HOME/.local/bin
file="$HOME/.local/bin/enable-interface-forwarding.sh"
cp "$config_files_root$file" "$file"
file="/etc/systemd/system/enable-interface-forwarding.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable enable-interface-forwarding.service

# Set up autohotspot service
file="/etc/systemd/system/autohotspot.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable autohotspot.service
file="/etc/systemd/system/autohotspot.timer"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable autohotspot.timer
file="$HOME/.local/bin/autohotspot.sh"
cp "$config_files_root$file" "$file"
