#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications, OS config files, and systemd
# system services for the PlanktoScope software distribution. This script integrates that pallet
# into the PlanktoScope OS's filesystem by installing Forklift and providing some systemd units
# which set up bind mounts and overlay filesystems to bootstrap the configs managed by Forklift.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Set up & stage local pallet

pallet_path="github.com/PlanktoScope/pallet-standard"
pallet_version="bc32ad9"
forklift plt switch --no-cache-img $pallet_path@$pallet_version

# Note: the pi user will only be able to run `forklift stage plan` and `forklift stage cache-img`
# without root permissions after a reboot, so we may need `sudo -E` here; I had tried running
# `newgrp docker` in the script to avoid the need for `sudo -E here`, but it doesn't work in the
# script here (even though it works after the script finishes, before rebooting):
FORKLIFT="forklift"
if [ -S /var/run/docker.sock ] && ! sudo -E docker ps 2&>1 > /dev/null; then
  sudo systemctl start docker.service
fi
if ! docker ps; then
  FORKLIFT="sudo -E forklift"
fi

$FORKLIFT stage plan
$FORKLIFT stage cache-img
next_pallet="$(basename $(forklift stage locate-bun next))"
# Applying the staged pallet (i.e. making Docker instantiate all the containers) significantly
# decreases first-boot time, by up to 30 sec for github.com/PlanktoScope/pallet-standard.
if ! $FORKLIFT stage apply; then
  echo "Warning: the next staged pallet could not be successfully applied. We'll try again on the next boot, since the pallet might require some files which will only be created during the next boot."
  # Reset the "apply-failed" status of the staged pallet to apply:
  forklift stage set-next --no-cache-img "$next_pallet"
fi
