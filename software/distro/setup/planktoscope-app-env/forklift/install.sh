#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications for the PlanktoScope software
# distribution

config_files_root=$(dirname $(realpath $BASH_SOURCE))
forklift_version="0.4.0"
pallet_version="3d864b"

curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_arm.tar.gz" \
  | tar -C $HOME/.local/bin -xz forklift
forklift="$HOME/.local/bin/forklift"
workspace="$HOME/.forklift"
$forklift --workspace $workspace plt clone github.com/PlanktoScope/pallet-standard@$pallet_version
$forklift --workspace $workspace plt cache-repo
# Note: cache-img downloads images even for disabled package deployments. We skip it to save disk
# space (because the node-red container image used by a test package is >100 MB, even though we
# don't need it yet), we don't yet have any packages in the pallet which someone might want to
# enable, and because we're running plt apply anyways - that command will download images as needed
# for each (enabled) package deployment.
# sudo -E $forklift --workspace $workspace plt cache-img
sudo -E $forklift --workspace $workspace plt apply
# Note: we apply the pallet immediately so that the first boot of the image won't be excessively
# slow (due to Docker Compose needing to create all the services from scratch rather than simply
# starting them).

# Apply pallet after Docker is initialized, because the system needs to be restarted after Docker is
# installed before the Docker service will be able to start successfully.
# Refer to https://www.reddit.com/r/raspberry_pi/comments/zblky6/comment/iytpp4g/ for details.
file="/etc/systemd/system/planktoscope-org.forklift-apply.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.forklift-apply.service
