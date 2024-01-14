#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications for the PlanktoScope software
# distribution

config_files_root=$(dirname $(realpath $BASH_SOURCE))
forklift_version="0.5.0"
pallet_version="fbf442db"

curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_arm.tar.gz" \
  | tar -C $HOME/.local/bin -xz forklift
workspace="$HOME"
forklift="$HOME/.local/bin/forklift --workspace $workspace"
$forklift plt clone --force github.com/PlanktoScope/pallet-standard@$pallet_version
$forklift plt cache-repo

# Note: this command must run with sudo even though the pi user has been added to the docker
# usergroup, because that change only works after starting a new login shell; and `newgrp docker`
# doesn't work either.
sudo -E $forklift plt cache-img --parallel # to save disk space, we don't cache images used by disabled package deployments

# The pallet must be applied during each startup because we're using Docker Compose, not Swarm Mode.
file="/etc/systemd/system/planktoscope-org.forklift-apply.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.forklift-apply.service
