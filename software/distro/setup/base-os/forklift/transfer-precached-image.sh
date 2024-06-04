#!/bin/bash -eux
image="$1"

precached_image="$HOME/.cache/containers/$(echo "$image" | sed "s~:~;~").tar"
docker image load --quiet < "$precached_image"
