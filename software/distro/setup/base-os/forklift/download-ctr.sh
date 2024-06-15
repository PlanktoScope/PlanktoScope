#!/bin/bash -eu
parent="$1"

config_files_root=$(dirname $(realpath $BASH_SOURCE))
version="$(cat "$config_files_root/ctr-version")"
arch="$(uname -m | sed -e 's~x86_64~amd64~' -e 's~aarch64~arm64~')"
tmp_bin="$(mktemp -d --tmpdir=/tmp bin.XXXXXXX)"

echo "Downloading ctr v$version ($arch) to $tmp_bin/ctr..."
curl -L "https://github.com/containerd/containerd/releases/download/v$version/containerd-static-$version-linux-${arch}.tar.gz" \
  | sudo tar -C "$tmp_bin" -xz bin/ctr

echo "Moving $tmp_bin/bin/ctr to $parent/ctr..."
mv "$tmp_bin/bin/ctr" "$parent/ctr" 2>/dev/null || sudo mv "$tmp_bin/bin/ctr" "$parent/ctr"
