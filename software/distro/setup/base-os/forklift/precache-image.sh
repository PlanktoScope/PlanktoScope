#!/bin/bash -eu
image="$1"

precached_image="$HOME/.cache/containers/$(echo "$image" | sed "s~:~;~").tar"

if [ -f "$precached_image" ]; then
  echo "Skipping $image, which was already downloaded to $precached_image!"
  exit 0
fi

mkdir -p "$(dirname "$precached_image")"

echo "Downloading $image to $precached_image..."
if ! skopeo copy --quiet \
  --override-arch "$(dpkg --print-architecture | sed -e 's~armhf~arm/v7~' -e 's~aarch64~arm64~')" \
  "docker://$image" "docker-archive:$precached_image:$image"
then
  echo "Encountered error, trying one more time to download $image..."
  rm "$precached_image"
  skopeo copy --quiet \
    --override-arch "$(dpkg --print-architecture | sed -e 's~armhf~arm/v7~' -e 's~aarch64~arm64~')" \
    "docker://$image" "docker-archive:$precached_image:$image"
fi
echo "Finished downloading $image!"
