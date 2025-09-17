#!/bin/bash -eux

../os/developer-mode/install-tailsale.sh

sudo apt install -y git ssh tmux
sudo systemctl enable --now ssh

# https://github.com/actions/runner/releases/tag/v2.327.1
cd ~
# Create a folder
mkdir actions-runner && cd actions-runner
# Download the latest runner package
curl -O -L https://github.com/actions/runner/releases/download/v2.327.1/actions-runner-linux-arm64-2.327.1.tar.gz
# Extract the installer
tar xzf ./actions-runner-linux-arm64-2.327.1.tar.gz

sudo tailsale up
