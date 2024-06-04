#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications, OS config files, and systemd
# system services for the PlanktoScope software distribution. This script integrates that pallet
# into the PlanktoScope OS's filesystem by installing Forklift and providing some systemd units
# which set up bind mounts and overlay filesystems to bootstrap the configs managed by Forklift.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install Forklift

forklift_version="0.7.3"

arch="$(dpkg --print-architecture | sed -e 's~armhf~arm~' -e 's~aarch64~arm64~')"
curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_${arch}.tar.gz" \
  | sudo tar -C /usr/bin -xz forklift
sudo mv /usr/bin/forklift "/usr/bin/forklift-${forklift_version}"
sudo ln -s "forklift-${forklift_version}" /usr/bin/forklift

# Prepare most of the necessary systemd units:
sudo cp $config_files_root/usr/lib/systemd/system/* /usr/lib/systemd/system/
sudo cp $config_files_root/usr/lib/systemd/system-preset/* /usr/lib/systemd/system-preset/
sudo systemctl preset forklift-apply.service
# Set up read-write filesystem overlays with forklift-managed layers for /etc and /usr
# (see https://docs.kernel.org/filesystems/overlayfs.html):
sudo systemctl preset \
  overlay-sysroot.service \
  bindro-run-forklift-stages-current.service \
  overlay-usr.service \
  overlay-etc.service \
  start-overlaid-units.service

# Make the stage store at /var/lib/forklift/stages available for non-root access in the current
# (i.e. default) user's default Forklift workspace, both in the current boot and subsequent boots:
local_stage_store="$HOME/.local/share/forklift/stages"
mkdir -p "$local_stage_store"
sudo mkdir -p /var/lib/forklift/stages
# TODO: maybe we should instead make a new "forklift" group which owns everything in
# /var/lib/forklift?
sudo chown $USER /var/lib/forklift/stages
sudo systemctl enable "bind-.local-share-forklift-stages@-home-$USER.service"
if ! sudo systemctl start "bind-.local-share-forklift-stages@-home-$USER.service" 2>/dev/null; then
  echo "Warning: the system's Forklift stage store is not mounted to $USER's Forklift stage store."
  echo "As long as you don't touch the Forklift stage store before the next boot, this is fine."
fi

# Clone a local pallet

pallet_path="github.com/PlanktoScope/pallet-standard"
pallet_version="bc32ad9"
forklift plt switch --no-cache-img $pallet_path@$pallet_version

# Pre-cache container images without Docker
docker_arch="$(dpkg --print-architecture | sed -e 's~armhf~arm/v7~' -e 's~aarch64~arm64~')"
sudo apt-get -y install skopeo
forklift plt ls-img |
  while IFS='' read -r image; do
    skopeo --override-arch "$docker_arch" copy "docker://$image" "containers-storage:$image"
  done
