#!/bin/bash -eu
parent="$1"

config_files_root=$(dirname $(realpath $BASH_SOURCE))
version="$(cat "$config_files_root/forklift-version")"
# Note: currently we use dpkg --print-architecture instead of uname -m because Forklift selects
# container image architectures for download based on the CPU target Forklift was compiled for, and
# we can't run arm64 containers on armhf Debian systems - even for Debian armhf systems running on
# arm64 CPUs.
arch="$(dpkg --print-architecture | sed -e 's~armhf~arm~' -e 's~aarch64~arm64~')"
tmp_bin="$(mktemp -d --tmpdir=/tmp bin.XXXXXXX)"

echo "Downloading forklift v$version ($arch) to $tmp_bin/forklift..."
curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$version/forklift_${version}_linux_${arch}.tar.gz" \
  | tar -C "$tmp_bin" -xz forklift

echo "Moving $tmp_bin/forklift to $parent/forklift..."
mv "$tmp_bin/forklift" "$parent/forklift" 2>/dev/null || sudo mv "$tmp_bin/forklift" "$parent/forklift"
