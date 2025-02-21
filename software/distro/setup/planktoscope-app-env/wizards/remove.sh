#!/bin/bash -eux

# Disable the first-boot graphical wizard
if ! sudo -E apt-get purge -y -o Dpkg::Progress-Fancy=0 piwiz; then
  echo "piwiz is already not installed, so no need to remove it!"
fi
