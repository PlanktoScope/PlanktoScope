#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications, OS config files, and systemd
# system services for the PlanktoScope software distribution. This script integrates that pallet
# into the PlanktoScope OS's filesystem by installing Forklift and providing some systemd units
# which set up bind mounts and overlay filesystems to bootstrap the configs managed by Forklift.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Install Forklift
"$config_files_root/download-forklift.sh" "/usr/bin"

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

# Clone & stage a local pallet

pallet_path="$(cat "$config_files_root/forklift-pallet")"
pallet_version="$(cat "$config_files_root/forklift-pallet-version")"
forklift --stage-store /var/lib/forklift/stages plt switch --no-cache-img $pallet_path@$pallet_version
sudo systemctl mask forklift-apply.service # we'll re-enable it after finishing setup in the VM

# Pre-download container images without Docker

echo "Downloading temporary tools to pre-download container images..."
tmp_bin="$(mktemp --directory bin.XXXXXXX)"
"$config_files_root/download-crane.sh" "$tmp_bin"
"$config_files_root/download-rush.sh" "$tmp_bin"

echo "Pre-downloading container images..."
container_platform="linux/$( \
  dpkg --print-architecture | sed -e 's~armhf~arm/v7~' -e 's~aarch64~arm64~' \
)"
export PATH="$tmp_bin:$PATH"
forklift plt ls-img | rush \
  "$config_files_root/precache-image.sh" \
    {} "$HOME/.cache/forklift/containers/oci-archives" "$container_platform"
