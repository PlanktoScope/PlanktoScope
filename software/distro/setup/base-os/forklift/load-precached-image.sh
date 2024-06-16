#!/bin/bash -eu
image="$1"
cache_path="$2" # e.g. ~/.cache/containers
ctr="$3" # e.g. /usr/bin/ctr

precached_image="$cache_path/$image.tar"

echo "Loading $image from $precached_image..."
# Note: we use `ctr` instead of `nerdctl` to import images because `nerdctl` doesn't discard blobs
# for layers unpacked by the snapshotter - so each container image is stored twice on the
# filesystem! The `--discard-unpacked-layers` flag of `ctr images import` solves this:
sudo $ctr --namespace moby images import "$precached_image"
rm "$precached_image"
