#!/bin/bash -eu
parent="$1"

config_files_root=$(dirname $(realpath $BASH_SOURCE))
version="$(cat "$config_files_root/nerdctl-version")"
# Note: we use dpkg --print-architecture instead of uname -m in order to make nerdctl match the
# architecture which containerd was installed as (containerd is installed with apt-get)
arch="$(dpkg --print-architecture | sed -e 's~armhf~arm-v7~' -e 's~aarch64~arm64~')"
tmp_bin="$(mktemp -d --tmpdir=/tmp bin.XXXXXXX)"

echo "Downloading nerdctl v$version ($arch) to $tmp_bin/nerdctl..."
curl -L "https://github.com/containerd/nerdctl/releases/download/v$version/nerdctl-${version}-linux-${arch}.tar.gz" \
  | sudo tar -C "$tmp_bin" -xz nerdctl

echo "Moving $tmp_bin/nerdctl to $parent/nerdctl..."
mv "$tmp_bin/nerdctl" "$parent/nerdctl" 2>/dev/null || sudo mv "$tmp_bin/nerdctl" "$parent/nerdctl"
