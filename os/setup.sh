#!/bin/bash -eu

# This is an installation script to bootstrap installation of PlanktoScope OS.
# It is meant to be run on a specific Raspberry OS Pi OS standard installation.

line=$(head -n 1 /etc/rpi-issue)
date="2025-10-01"
expected="Raspberry Pi reference $date"

if [ "$line" != "$expected" ]; then
  echo "ERROR: Only Raspberry Pi OS $date is supported."
  exit 1
fi

cd /home/pi
sudo apt install -y git just
if cd PlanktoScope; then git pull; else git clone https://github.com/PlanktoScope/PlanktoScope.git; fi
cd PlanktoScope
just
./os/postinstall.sh
