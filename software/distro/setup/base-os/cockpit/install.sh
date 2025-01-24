#!/bin/bash -eux
# Cockpit enables system administration from a web browser.

# Install cockpit
sudo -E apt-get install -y --no-install-recommends -o Dpkg::Progress-Fancy=0 \
  cockpit cockpit-networkmanager
