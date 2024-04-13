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
sudo -E forklift stage cache-img --parallel
# Note: the pallet must be applied during each startup because we're using Docker Compose rather
# than Swarm Mode:
unit="forklift-apply.service"
sudo cp "$config_files_root/usr/lib/systemd/system/$unit" "/usr/lib/systemd/system/$unit"
sudo ln -s "../$unit" "/usr/lib/systemd/system/multi-user.target.wants/$unit"

# Move the stage store to /var/lib/forklift/stages, but keep it available for non-root access in the
# current (i.e. default) user's default Forklift workspace:
sudo mkdir -p /var/lib/forklift
sudo mv $FORKLIFT_WORKSPACE/.local/share/forklift/stages /var/lib/forklift/stages
unit="bind-.local-share-forklift-stages@.service"
sudo cp "$config_files_root/usr/lib/systemd/system/$unit" "/usr/lib/systemd/system/$unit"
sudo ln -s "../$unit" "/usr/lib/systemd/system/multi-user.target.wants/bind-.local-share-forklift-stages@-home-$USER.service"
sudo systemctl start bind-.local-share-forklift-stages@-home-$USER.service

# Set up read-write filesystem overlays with forklift-managed layers for /etc and /usr
# (see https://docs.kernel.org/filesystems/overlayfs.html):
unit="bindro-sysroot.service"
sudo cp "$config_files_root/usr/lib/systemd/system/$unit" "/usr/lib/systemd/system/$unit"
sudo ln -s "../$unit" "/usr/lib/systemd/system/local-fs.target.wants/$unit"
unit="overlay-run-forklift-stages-current.service"
sudo cp "$config_files_root/usr/lib/systemd/system/$unit" "/usr/lib/systemd/system/$unit"
sudo ln -s "../$unit" "/usr/lib/systemd/system/local-fs.target.wants/$unit"
# Note: we don't move /etc to /usr/etc because that makes it more complicated/difficult to ensure
# that systemd correctly initializes /etc/machine-id on first boot (which is needed to make journald
# work, e.g. for viewing service logs), and because we need some /etc files anyways (notably,
# /etc/fstab and maybe also /etc/systemd/system/*.target.wants) before we can bring up the overlay
# mount; instead, we just bind-mount /etc to /usr/etc as the base layer for an overlay at /etc
# (see also: https://www.spinics.net/lists/systemd-devel/msg03771.html,
# https://bootlin.com/blog/systemd-read-only-rootfs-and-overlay-file-system-over-etc/, and
# https://community.toradex.com/t/automount-overlay-for-etc/15529/8):
unit="overlay-etc.service"
sudo cp "$config_files_root/usr/lib/systemd/system/$unit" "/usr/lib/systemd/system/$unit"
sudo ln -s "../$unit" "/usr/lib/systemd/system/local-fs.target.wants/$unit"
unit="overlay-usr.service"
sudo cp "$config_files_root/usr/lib/systemd/system/$unit" "/usr/lib/systemd/system/$unit"
sudo ln -s "../$unit" "/usr/lib/systemd/system/local-fs.target.wants/$unit"
# Note: we don't activate these overlays right now because we want to let subsequent setup scripts
# make changes directly to the base layers of /etc and /usr for the OS image.
