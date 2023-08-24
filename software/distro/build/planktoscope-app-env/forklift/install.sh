#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications for the PlanktoScope software
# distribution

config_files_root=$(dirname $(realpath $BASH_SOURCE))
forklift_version="0.3.1"
pallet_version="44f7c59"

curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_arm.tar.gz" \
  | tar -C /home/pi/.local/bin -xz forklift
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt clone github.com/PlanktoScope/pallet-standard@$pallet_version
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt cache-repo
sudo -E /home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt cache-img
sudo -E /home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt apply
