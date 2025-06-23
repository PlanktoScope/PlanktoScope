#!/bin/bash -eux
# The base OS tools provide some useful command-line utilities for the rest of the scripted setup
# process, and for user-driven setup after installation.

# Install some tools for a nicer command-line experience over ssh
# Note: we don't want to do an apt-get upgrade because then we'd have no way to ensure the same set
# of package versions for existing packages if we run the script at different times. Also, it causes
# some weirdness with the Docker installation.
sudo -E apt-get install -y -o DPkg::Lock::Timeout=60 -o Dpkg::Progress-Fancy=0 \
  vim byobu git curl

# Install some tools for dealing with captive portals
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  w3m lynx

# Install some tools for troubleshooting networking stuff
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  net-tools bind9-dnsutils netcat-openbsd nmap avahi-utils
