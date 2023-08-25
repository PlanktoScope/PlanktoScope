#!/bin/bash -eux
# The base OS tools enable basic operation of the OS, and provide generalized mechanisms for
# bootstrapping further software (e.g. user applications) to be installed afterwards.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install some tools for a nicer command-line experience over ssh
# Note: we don't want to do an apt-get upgrade because then we'd have no way to ensure the same set
# of package versions for existing packages if we run the script at different times.
sudo apt-get update -y
sudo apt-get install -y vim byobu git

# Install some tools for dealing with captive portals
sudo apt-get install -y w3m
# Note: we don't install browsh (which requires firefox-esr) because it adds ~200-300 MB of
# dependencies in the base image. Users who need browsh should instead use the Docker image from
# https://hub.docker.com/r/browsh/browsh

# Install Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/raspbian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/raspbian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y # get the list of packages from the docker repo
VERSION_STRING=5:24.0.5-1~raspbian.11~bullseye
# The following command will fail with a post-install error if the system installed kernel updates
# via apt upgrade but was not rebooted before installing docker-ce; however, even if this error
# is reported, docker will work after reboot.
# Refer to https://www.reddit.com/r/raspberry_pi/comments/zblky6/comment/iytpp4g/ for details.
sudo apt-get install -y \
  docker-ce=$VERSION_STRING docker-ce-cli=$VERSION_STRING \
  containerd.io docker-compose-plugin
sudo apt-get remove -y docker-buildx-plugin

# Install cockpit
sudo apt-get update -y
sudo apt-get install -y cockpit
# We remove the NetworkManager integration because trying to use it will break the PlanktoScope's
# current networking configuration.
sudo apt-get remove -y cockpit-networkmanageer
sudo mkdir -p /etc/cockpit/
file="/etc/cockpit/cockpit.conf"
sudo cp "$config_files_root$file" "$file"
