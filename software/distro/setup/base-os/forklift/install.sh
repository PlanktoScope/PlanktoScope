#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications, OS config files, and systemd
# system services for the PlanktoScope software distribution.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install Forklift

forklift_version="0.6.0"
pallet_path="github.com/PlanktoScope/pallet-standard"
pallet_version="v2024.0.0-alpha.1"

arch="$(dpkg --print-architecture | sed -e 's/armhf/arm/' -e 's/aarch64/arm64/')"
curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_${arch}.tar.gz" \
  | sudo tar -C /usr/bin -xz forklift
sudo mv /usr/bin/forklift "/usr/bin/forklift-${forklift_version}"
sudo ln -s "/usr/bin/forklift-${forklift_version}" /usr/bin/forklift

# Set up local pallet

workspace="$HOME"
forklift --workspace $workspace plt clone --force $pallet_path@$pallet_version
forklift --workspace $workspace plt cache-repo

# Note: this command must run with sudo even though the pi user has been added to the docker
# usergroup, because that change only works after starting a new login shell; and `newgrp docker`
# doesn't work either:
sudo -E forklift --workspace $workspace plt cache-img --parallel # to save disk space, we don't cache images used by disabled package deployments

# Note: the pallet must be applied during each startup because we're using Docker Compose rather
# than Swarm Mode:
file="/usr/lib/systemd/system/forklift-apply.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable forklift-apply.service

# Copy files from /etc to /usr/etc for a filesystem overlay at /etc, but keep a copy of everything
# in `/etc` because it seems to be needed for journald to work properly:
sudo sh -c " printf 'uninitialized\n' > /etc/machine-id"
sudo cp -r /etc /usr/etc
sudo mount --bind /usr/etc /etc

# Set up overlay for /etc
file="/usr/lib/systemd/system/etc.mount"
sudo cp "$config_files_root$file" "$file"
# We enable the mount directly via symlink because `systemctl enable` makes the symlink in `/etc`,
# which we've bind-mounted to `/usr/etc` (so it won't show up at boot in `/etc` before the mount is
# started - and the purpose of the mount is to use `/usr/etc` for `/etc`):
sudo ln -s "$file" /usr/lib/systemd/system/local-fs.target.wants/etc.mount
sudo mkdir -p /var/lib/forklift/exports/next/overlays/etc
sudo mkdir -p /var/lib/overlays/overrides/etc
sudo mkdir -p /var/lib/overlays/workdirs/etc
