#!/bin/bash -eu
image="$1"
cache_path="$2" # e.g. ~/.cache/containers
platform="$3" # e.g. `linux/arm64`

precached_image="$cache_path/$image.tar"

if [ -f "$precached_image" ]; then
  echo "Skipping $image, which was already downloaded to $precached_image!"
  exit 0
fi

crane="crane"
if ! mkdir -p "$(dirname "$precached_image")"; then
  sudo mkdir -p "$(dirname "$precached_image")"
  crane="$sudo crane"
fi

echo "Downloading $image to $precached_image..."
# We pull images as Docker (legacy) tarballs so that they can be inspected with `dive` (which does
# not support OCI tarballs) - see https://github.com/google/go-containerregistry/issues/621 for
# details:
if ! $crane --platform "$platform" pull --format legacy "$image" "$precached_image"
then
  echo "Encountered error, trying one more time to download $image..."
  rm -f "$precached_image" || sudo rm -f "$precached_image"
  $crane --platform "$platform" pull --format legacy "$image" "$precached_image"
fi
echo "Finished downloading $image!"
