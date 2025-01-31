#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications, OS config files, and systemd
# system services for the PlanktoScope software distribution. This script integrates that pallet
# into the PlanktoScope OS's filesystem by installing Forklift and providing some systemd units
# which set up bind mounts and overlay filesystems to bootstrap the configs managed by Forklift.

config_files_root=$(dirname "$(realpath "$BASH_SOURCE")")

# Install Forklift
"$config_files_root/download-forklift.sh" "/usr/bin"

# Add the necessary systemd units (but we don't enable them until booted setup):
sudo cp "$config_files_root"/usr/lib/systemd/system/* /usr/lib/systemd/system/
sudo cp "$config_files_root"/usr/lib/systemd/system-preset/* /usr/lib/systemd/system-preset/

# Make the stage store at /var/lib/forklift/stages available for easy access in the root user's
# default Forklift workspace, both in the current boot and subsequent boots (staged pallet bundles
# must be created with root user ownership because NetworkManager requires its network connection
# files to have root ownership; and because forklift's system administration operations belong in
# the superuser security domain):
sudo mkdir -p "/root/.local/share/forklift/stages"
sudo mkdir -p /var/lib/forklift/stages
sudo systemctl enable "bind-.local-share-forklift-stages@-root.service"
if ! sudo systemctl start "bind-.local-share-forklift-stages@-root.service" 2>/dev/null; then
  echo "Warning: the system's Forklift stage store is not mounted to the root user's Forklift stage store."
  echo "As long as you don't touch the Forklift stage store before the next boot, this is fine."
fi

# Clone & stage a local pallet
pallet_path="$(cat "$config_files_root/forklift-pallet")"
pallet_version="$(cat "$config_files_root/forklift-pallet-version")"
sudo forklift --stage-store /var/lib/forklift/stages plt switch --no-cache-img "$pallet_path@$pallet_version"
sudo forklift --stage-store /var/lib/forklift/stages stage add-bundle-name factory-reset next

# Set up Forklift upgrade checks
pallet_upgrade_version_query="$(cat "$config_files_root/forklift-pallet-upgrade-version-query")"
sudo forklift pallet set-upgrade-query "@$pallet_upgrade_version_query"

# Pre-download container images without Docker

echo "Downloading temporary tools to pre-download container images..."
tmp_bin="$(mktemp -d --tmpdir=/tmp bin.XXXXXXX)"
"$config_files_root/download-crane.sh" "$tmp_bin"
"$config_files_root/download-rush.sh" "$tmp_bin"
export PATH="$tmp_bin:$PATH"

echo "Pre-downloading container images..."
container_platform="linux/$(
  dpkg --print-architecture | sed -e 's~armhf~arm/v7~' -e 's~aarch64~arm64~'
)"
export PATH="$tmp_bin:$PATH"
sudo forklift plt ls-img |
  rush "$config_files_root/precache-image.sh" \
    {} "/root/.cache/forklift/containers/docker-archives" "$container_platform"

echo "Preparing to load pre-downloaded container images..."
"$config_files_root/ensure-docker.sh"

echo "Loading pre-downloaded container images..."
sudo forklift plt ls-img |
  rush "$config_files_root/load-precached-image.sh" \
    {} "/root/.cache/forklift/containers/docker-archives"

# Prepare to apply the local pallet

FORKLIFT="sudo forklift --stage-store /var/lib/forklift/stages"

# Make a temporary file which may be required by some Docker Compose apps in the pallet, just so
# that those Compose apps can be successfully created (this is a rather dirty hack/workaround):
echo "setup" | sudo tee /run/machine-name

# Applying the staged pallet (i.e. making Docker instantiate all the containers) significantly
# decreases first-boot time, by up to 30 sec for github.com/PlanktoScope/pallet-standard.
if ! "$FORKLIFT" stage apply; then
  echo "The staged pallet couldn't be applied; we'll try again now..."
  # Reset the "apply-failed" status of the staged pallet to apply:
  "$FORKLIFT" stage set-next --no-cache-img next
  if ! "$FORKLIFT" stage apply; then
    echo "Warning: the next staged pallet could not be successfully applied. We'll try again on the next boot, since the pallet might require some files which will only be created during the next boot."
    # Reset the "apply-failed" status of the staged pallet to apply:
    "$FORKLIFT" stage set-next --no-cache-img next
    echo "Checking the plan for applying the staged pallet..."
    "$FORKLIFT" stage plan
  fi
fi

# Use forklift on future boot sequences
sudo systemctl preset forklift-apply.service
# Set up read-write filesystem overlays with forklift-managed layers for /etc and /usr
# (see https://docs.kernel.org/filesystems/overlayfs.html):
sudo systemctl preset \
  overlay-sysroot.service \
  bindro-run-forklift-stages-current.service \
  overlay-usr.service \
  overlay-etc.service \
  start-overlaid-units.service
