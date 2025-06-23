#!/bin/bash -eux
parent="$1"

config_files_root=$(dirname $(realpath $BASH_SOURCE))
version="$(cat "$config_files_root/crane-version")"
arch="$(uname -m | sed -e 's~aarch64~arm64~')"
tmp_bin="$(mktemp -d --tmpdir=/tmp bin.XXXXXXX)"

echo "Downloading crane v$version ($arch) to $tmp_bin/crane..."
curl -L "https://github.com/google/go-containerregistry/releases/download/v$version/go-containerregistry_Linux_${arch}.tar.gz" \
  | tar -C "$tmp_bin" -xz crane

echo "Moving $tmp_bin/crane to $parent/crane..."
mv "$tmp_bin/crane" "$parent/crane" 2>/dev/null || sudo mv "$tmp_bin/crane" "$parent/crane"
