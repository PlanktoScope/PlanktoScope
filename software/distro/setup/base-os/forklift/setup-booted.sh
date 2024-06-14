#!/bin/bash -eux

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# TODO: can we run this script in an unbooted container by just starting /usr/bin/containerd?

# Load pre-downloaded container images for the local pallet into containerd's image storage

echo "Downloading temporary tools to load pre-downloaded container images into Docker..."
tmp_bin="$(mktemp -d --tmpdir=/tmp bin.XXXXXXX)"
"$config_files_root/download-rush.sh" "$tmp_bin"
"$config_files_root/download-nerdctl.sh" "$tmp_bin"
export PATH="$tmp_bin:$PATH"

echo "Loading pre-downloaded container images into Docker..."
forklift plt ls-img | rush \
  "$config_files_root/load-precached-image.sh" {} "$HOME/.cache/forklift/containers/docker-archives"

# TODO: make this compatible with running setup scripts on a real RPi without reboots, e.g. by
# restarting Docker after setting the config to use containerd for image storage
echo "TODO: implement remaining stuff"
exit 42
