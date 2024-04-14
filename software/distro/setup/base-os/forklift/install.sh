#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications, OS config files, and systemd
# system services for the PlanktoScope software distribution. This script integrates that pallet
# into the PlanktoScope OS's filesystem by installing Forklift and providing some systemd units
# which set up bind mounts and overlay filesystems to bootstrap the configs managed by Forklift.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install Forklift

forklift_version="0.7.0-alpha.3"
pallet_path="github.com/PlanktoScope/pallet-standard"
pallet_version="feature/file-exports"

arch="$(dpkg --print-architecture | sed -e 's/armhf/arm/' -e 's/aarch64/arm64/')"
curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_${arch}.tar.gz" \
  | sudo tar -C /usr/bin -xz forklift
sudo mv /usr/bin/forklift "/usr/bin/forklift-${forklift_version}"
sudo ln -s "forklift-${forklift_version}" /usr/bin/forklift

# Set up & stage local pallet

FORKLIFT_WORKSPACE="$HOME"
forklift plt switch --no-cache-img $pallet_path@$pallet_version
# Note: the pi user will only be able to run `forklift stage plan` and `forklift stage cache-img`
# without root permissions after a reboot, so we need `sudo -E` here; I tried running
# `newgrp docker` in the script to avoid the need for `sudo -E here`, but it doesn't work in the
# script here (even though it works after the script finishes, before rebooting):
sudo -E forklift stage plan --parallel
# FIXME: re-enable this
#sudo -E forklift stage cache-img --parallel

# Prepare most of the necessary systemd units:
sudo cp $config_files_root/usr/lib/systemd/system/* /usr/lib/systemd/system/
sudo cp $config_files_root/usr/lib/systemd/system-preset/* /usr/lib/systemd/system-preset/
sudo systemctl preset forklift-apply.service
# Set up read-write filesystem overlays with forklift-managed layers for /etc and /usr
# (see https://docs.kernel.org/filesystems/overlayfs.html):
sudo systemctl preset \
  bindro-sysroot.service \
  overlay-run-forklift-stages-current.service \
  overlay-usr.service \
  overlay-etc.service \
  start-overlaid-units.service

# Move the stage store to /var/lib/forklift/stages, but keep it available for non-root access in the
# current (i.e. default) user's default Forklift workspace:
sudo mkdir -p /var/lib/forklift
sudo mv $FORKLIFT_WORKSPACE/.local/share/forklift/stages /var/lib/forklift/stages
sudo systemctl enable "bind-.local-share-forklift-stages@-home-$USER.service" --now
