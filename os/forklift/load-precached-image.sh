#!/bin/bash -eux
image="$1"
cache_path="$2" # e.g. ~/.cache/containers

precached_image="$cache_path/$image.tar"

echo "Loading $image from $precached_image..."
sudo docker image load --quiet --input "$precached_image"
sudo rm "$precached_image"
