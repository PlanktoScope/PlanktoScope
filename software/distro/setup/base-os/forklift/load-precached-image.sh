#!/bin/bash -eu
image="$1"
cache_path="$2" # e.g. ~/.cache/containers
loader="$3" # either `docker` or `nerdctl`

precached_image="$cache_path/$image.tar"

echo "Loading $image from $precached_image with $loader..."
sudo $loader image load --quiet < "$precached_image"
rm "$precached_image"
