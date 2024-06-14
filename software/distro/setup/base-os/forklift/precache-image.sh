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
if ! mkdir -p "$cache_path"; then
  sudo mkdir -p "$cache_path"
  crane="$sudo crane"
fi

echo "Downloading $image to $precached_image..."
if ! $crane --platform "$platform" pull --format=oci "$image" "$precached_image"
then
  echo "Encountered error, trying one more time to download $image..."
  rm -f "$precache_image" || sudo rm -f "$precached_image"
  $crane --platform "$platform" pull --format=oci "$image" "$precached_image"
fi
echo "Finished downloading $image!"
