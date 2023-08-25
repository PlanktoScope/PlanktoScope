#!/bin/bash -eux
# The Forklift pallet github.com/PlanktoScope/pallet-standard provides the standard configuration of
# Forklift package deployments of Docker containerized applications for the PlanktoScope software
# distribution

config_files_root=$(dirname $(realpath $BASH_SOURCE))
forklift_version="0.3.1"
pallet_version="5018c89e4ccab7f55847433bd6f52c789b0bda35"

curl -L "https://github.com/PlanktoScope/forklift/releases/download/v$forklift_version/forklift_${forklift_version}_linux_arm.tar.gz" \
  | tar -C /home/pi/.local/bin -xz forklift
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt clone github.com/PlanktoScope/pallet-standard@$pallet_version
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt cache-repo
sudo -E /home/pi/.local/bin/forklift --workspace /home/pi/.forklift plt cache-img
# Note: we don't apply the pallet immediately because the Docker service won't work properly until a
# reboot. Forklift apply doesn't actually cause the containers to exist after a reboot.

# Apply pallet after Docker is initialized, because the system needs to be restarted after Docker is
# installed before the Docker service will be able to start successfully.
# Refer to https://www.reddit.com/r/raspberry_pi/comments/zblky6/comment/iytpp4g/ for details.
file="/etc/systemd/system/forklift-apply.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable forklift-apply.service
