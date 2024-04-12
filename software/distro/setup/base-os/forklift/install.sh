#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications, OS config files, and systemd
# system services for the PlanktoScope software distribution.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install Forklift

forklift_version="0.7.0-alpha.0"
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
forklift --workspace $workspace plt stage

# Note: these command must run with sudo even though the pi user has been added to the docker
# usergroup, because that change only works after starting a new login shell; and `newgrp docker`
# doesn't work either:
sudo -E forklift --workspace $workspace stage plan
sudo -E forklift --workspace $workspace stage cache-img --parallel

# Note: the pallet must be applied during each startup because we're using Docker Compose rather
# than Swarm Mode:
file="/usr/lib/systemd/system/forklift-apply.service"
sudo cp "$config_files_root$file" "$file"
sudo ln -s "$file" /usr/lib/systemd/system/multi-user.target.wants/forklift-apply.service

# Set up overlays for /etc and /usr/local
file="/usr/lib/systemd/system/mount-sysroot.service"
sudo cp "$config_files_root$file" "$file"
sudo ln -s "$file" /usr/lib/systemd/system/mount-local-fs.target.wants/sysroot.service
file="/usr/lib/systemd/system/mount-run-forklift-stages-current.service"
sudo cp "$config_files_root$file" "$file"
sudo ln -s "$file" /usr/lib/systemd/system/local-fs.target.wants/mount-run-forklift-stages-current.service
# Note: we don't move /etc into /usr because that makes it more complicated/difficult to ensure
# that systemd correctly initializes /etc/machine-id on first boot (which is needed to make journald
# work, e.g. for viewing service logs), and because we need some /etc files anyways (notably,
# /etc/fstab and maybe also /etc/systemd/system/*.target.wants) before we can bring up the overlay
# mount; instead, we just bind-mount /etc to /usr/etc as the base layer for an overlay at /etc
# (see also: https://www.spinics.net/lists/systemd-devel/msg03771.html,
# https://bootlin.com/blog/systemd-read-only-rootfs-and-overlay-file-system-over-etc/, and
# https://community.toradex.com/t/automount-overlay-for-etc/15529/8):
file="/usr/lib/systemd/system/mount-etc-overlay.service"
sudo cp "$config_files_root$file" "$file"
sudo ln -s "$file" /usr/lib/systemd/system/local-fs.target.wants/mount-etc-overlay.service
file="/usr/lib/systemd/system/usr-local.mount"
sudo cp "$config_files_root$file" "$file"
sudo ln -s "$file" /usr/lib/systemd/system/local-fs.target.wants/usr-local.mount

# Bind-mount /var/lib/forklift/stages into the pi user's default Forklift workspace
sudo mkdir -p /var/lib/forklift
sudo mv $workspace/.local/share/forklift/stages /var/lib/forklift/stages
file="/usr/lib/systemd/system/home-pi-.local-share-forklift-stages.mount"
sudo cp "$config_files_root$file" "$file"
sudo ln -s "$file" /usr/lib/systemd/system/local-fs.target.wants/home-pi-.local-share-forklift-stages.mount
sudo systemctl start home-pi-.local-share-forklift-stages.mount
