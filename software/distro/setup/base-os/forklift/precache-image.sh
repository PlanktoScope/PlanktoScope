#!/bin/bash -eux
image="$1"

precached_image="$HOME/.cache/containers/$(echo "$image" | sed "s~:~;~").tar"
mkdir -p "$(dirname "$precached_image")"

skopeo copy --quiet \
  --override-arch "$(dpkg --print-architecture | sed -e 's~armhf~arm/v7~' -e 's~aarch64~arm64~')" \
  "docker://$image" "docker-archive:$precached_image:$image"
