#!/bin/bash -eu

# This is an installation script to bootstrap installation of PlanktoScope OS.
# It is meant to be run on top of Raspberry OS Pi OS.

sudo mount -o remount,rw /boot/firmware
sudo apt update -y
sudo apt install -y git just
cd /opt
if cd PlanktoScope; then
    git pull
else
    sudo mkdir PlanktoScope
    sudo chown pi:pi PlanktoScope
    git clone https://github.com/fairscope/PlanktoScope.git
    cd PlanktoScope
fi
git submodule update --init
just
./os/postinstall.sh

echo "✅ Setup complete. Please reboot."
