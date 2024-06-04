#!/bin/bash -eu
image="$1"

precached_image="$HOME/.cache/containers/$(echo "$image" | sed "s~:~;~").tar"

echo "Loading $image from $precached_image..."
docker image load --quiet < "$precached_image"
