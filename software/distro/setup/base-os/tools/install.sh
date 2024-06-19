#!/bin/bash -eux
# The base OS tools provide some useful command-line utilities for the rest of the scripted setup
# process, and for user-driven setup after installation.

# Install some tools for a nicer command-line experience over ssh
# Note: we don't want to do an apt-get upgrade because then we'd have no way to ensure the same set
# of package versions for existing packages if we run the script at different times. Also, it causes
# some weirdness with the Docker installation.
sudo apt-get install -y -o DPkg::Lock::Timeout=60 -o Dpkg::Progress-Fancy=0 \
  vim byobu git curl

# Install some tools for dealing with captive portals
sudo apt-get install -y -o Dpkg::Progress-Fancy=0 \
  w3m lynx

# Prepare tool to generate machine names based on serial numbers
# Note: the tool itself is deployed/managed by Forklift.
# TODO: remove this by updating the Node-RED frontend and Python backend:
# Add a symlink at /var/lib/planktoscope/machine-name for backwards-compatibility with the Node-RED
# frontend and Python backend, which are not yet updated to check /run/machine-name instead:
sudo mkdir -p /var/lib/planktoscope
sudo rm -f /var/lib/planktoscope/machine-name
sudo ln -s /run/machine-name /var/lib/planktoscope/machine-name
