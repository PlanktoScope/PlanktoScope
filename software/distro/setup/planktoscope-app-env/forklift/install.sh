#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications for the PlanktoScope software
# distribution

config_files_root=$(dirname $(realpath $BASH_SOURCE))
forklift_version="0.4.0"
pallet_version="4fd9a86"

curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_arm.tar.gz" \
  | tar -C /home/pi/.local/bin -xz forklift
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt clone github.com/PlanktoScope/pallet-standard@$pallet_version
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt cache-repo
sudo -E /home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt cache-img
sudo -E /home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt apply
# Note: we apply the pallet immediately so that the first boot of the image won't be excessively
# slow (due to Docker Compose needing to create all the services from scratch rather than simply
# starting them).

# Apply pallet after Docker is initialized, because the system needs to be restarted after Docker is
# installed before the Docker service will be able to start successfully.
# Refer to https://www.reddit.com/r/raspberry_pi/comments/zblky6/comment/iytpp4g/ for details.
file="/etc/systemd/system/planktoscope-org.forklift-apply.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable planktoscope-org.forklift-apply.service
