#!/bin/bash -eux
# The Forklift environment provides the standard configuration of Pallet package deployments of
# Docker containerized applications for the PlanktoScope software distribution

curl -L https://github.com/PlanktoScope/forklift/releases/download/v0.1.5/forklift_0.1.5_linux_arm.tar.gz | tar -C /home/pi/.local/bin -xz forklift
forklift --workspace /home/pi/.forklift env clone github.com/PlanktoScope/pallets-env@cdbe27e
forklift --workspace /home/pi/.forklift env cache
# TODO: maybe we should pre-cache the Docker container images and instead deploy on first boot?
sudo -E /home/pi/.local/bin/forklift --workspace /home/pi/.forklift env deploy
