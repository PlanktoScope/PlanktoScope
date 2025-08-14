#!/bin/bash -eux

# TODO: On Debian 13 we can use the just package from Debian repositories

# Copied from
# https://docs.makedeb.org/prebuilt-mpr/getting-started/#setting-up-the-repository
# https://github.com/casey/just/blob/743e700d8bb5ae66b5d2f061461a4964ba124be3/README.md#linux
wget -qO - 'https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub' | gpg --dearmor | sudo tee /usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg 1> /dev/null
echo "deb [arch=all,$(dpkg --print-architecture) signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] https://proget.makedeb.org prebuilt-mpr $(lsb_release -cs)" | sudo tee /etc/apt/sources.list.d/prebuilt-mpr.list
sudo apt update
sudo apt install -y just
