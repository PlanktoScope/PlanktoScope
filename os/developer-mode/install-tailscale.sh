#!/bin/bash -eux

# https://tailscale.com/download/linux/debian-trixie

curl -fsSL https://pkgs.tailscale.com/stable/raspbian/trixie.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg > /dev/null
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/trixie.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt update
sudo apt install -y tailscale
sudo systemctl reenable tailscaled
sudo systemctl restart tailscaled
