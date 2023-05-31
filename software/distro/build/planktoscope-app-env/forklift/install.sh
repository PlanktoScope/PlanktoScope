#!/bin/bash -eux
# The Forklift environment provides the standard configuration of Pallet package deployments of
# Docker containerized applications for the PlanktoScope software distribution

curl -L https://github.com/PlanktoScope/forklift/releases/download/v0.1.6/forklift_0.1.6_linux_arm.tar.gz | tar -C /home/pi/.local/bin -xz forklift
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift env clone github.com/PlanktoScope/pallets-env@5fb6f83
/home/pi/.local/bin/forklift --workspace /home/pi/.forklift env cache-repo
sudo -E /home/pi/.local/bin/forklift --workspace /home/pi/.forklift env cache-img

# Deploy environment after Docker Swarm is initialized
file="/etc/systemd/system/first-boot-forklift-deploy.service"
sudo cp "$config_files_root$file" "$file"
sudo systemctl enable first-boot-forklift-deploy.service
