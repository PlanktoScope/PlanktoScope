#!/bin/bash -eux
parent="$1"

config_files_root=$(dirname $(realpath $BASH_SOURCE))
version="$(cat "$config_files_root/rush-version")"
arch="$(uname -m | sed -e 's~x86_64~amd64~' -e 's~aarch64~arm64~')"
tmp_bin="$(mktemp -d --tmpdir=/tmp bin.XXXXXXX)"

echo "Downloading rush v$version ($arch) to $tmp_bin/rush..."
curl -L "https://github.com/shenwei356/rush/releases/download/v$version/rush_linux_${arch}.tar.gz" \
  | sudo tar -C "$tmp_bin" -xz rush

echo "Moving $tmp_bin/rush to $parent/rush..."
mv "$tmp_bin/rush" "$parent/rush" 2>/dev/null || sudo mv "$tmp_bin/rush" "$parent/rush"
