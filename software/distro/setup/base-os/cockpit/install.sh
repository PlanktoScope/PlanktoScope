#!/bin/bash -eux
# Cockpit enables system administration from a web browser.

# Install cockpit
sudo apt-get install -y --no-install-recommends -o Dpkg::Progress-Fancy=0 \
  cockpit
# TODO: after we switch to NetworkManager, add cockpit-networkmanager
