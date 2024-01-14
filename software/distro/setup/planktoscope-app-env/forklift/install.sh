#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications for the PlanktoScope software
# distribution

config_files_root=$(dirname $(realpath $BASH_SOURCE))
forklift_version="0.5.0"
pallet_version="c84c827"

curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_arm.tar.gz" \
  | tar -C $HOME/.local/bin -xz forklift
workspace="$HOME/.forklift"
forklift="$HOME/.local/bin/forklift --workspace $workspace"
if [ -d "$workspace" ]; then
  $forklift plt rm
fi
$forklift plt clone github.com/PlanktoScope/pallet-standard@$pallet_version
$forklift plt cache-repo

# Note: the below commands must run with sudo even though the pi user has been added to the docker
# usergroup, because that change only works after starting a new login shell; and `newgrp docker`
# doesn't work either.
sudo -E $forklift plt cache-img --parallel # to save disk space, don't cache images used by disabled package deployments
# Note: we apply the pallet immediately so that the first boot of the image won't be excessively
# slow (due to Docker Compose needing to create all the services from scratch rather than simply
# starting them).
sudo -E $forklift plt apply --parallel

# The pallet must be applied during each startup because we're using Docker Compose, not Swarm Mode.
file="/etc/systemd/system/planktoscope-org.forklift-apply.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.forklift-apply.service
