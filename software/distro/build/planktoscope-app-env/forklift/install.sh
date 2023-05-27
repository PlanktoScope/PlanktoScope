#!/bin/bash -eux
# The Forklift environment provides the standard configuration of Pallet package deployments of
# Docker containerized applications for the PlanktoScope software distribution

curl -L https://github.com/PlanktoScope/forklift/releases/download/v0.1.5/forklift_0.1.5_linux_arm.tar.gz | tar -C /home/pi/.local/bin -xz forklift
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift env clone github.com/PlanktoScope/pallets-env@cdbe27e
# FIXME: we need to pre-cache the Docker container images so that we don't need internet when we deploy the packages. Or we should just use Docker Compose.
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift env cache

# Deploy environment after Docker Swarm is initialized
file="/etc/systemd/system/first-boot-forklift-deploy.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable first-boot-forklift-deploy.service
