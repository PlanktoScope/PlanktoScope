#!/bin/bash -eux
# Docker enables deployment of containerized applications.

config_files_root=$(dirname "$(realpath "$BASH_SOURCE")")

sudo install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  curl -fsSL "https://download.docker.com/linux/debian/gpg" |
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
fi
sudo chmod a+r /etc/apt/keyrings/docker.gpg
DISTRO_VERSION_CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg]" \
  "https://download.docker.com/linux/debian $DISTRO_VERSION_CODENAME stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo -E apt-get update -y -o Dpkg::Progress-Fancy=0 # get the list of packages from the docker repo
# The following command may fail with a post-install error if the system installed kernel updates
# via apt upgrade but was not rebooted before installing docker-ce; however, even if this error
# is reported, docker will work after reboot.
# Refer to https://www.reddit.com/r/raspberry_pi/comments/zblky6/comment/iytpp4g/ for details.
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo -E apt-get remove -y -o Dpkg::Progress-Fancy=0 \
  docker-buildx-plugin

# Allow running Docker commands without sudo. Before the next reboot, subsequent setup scripts will
# still need to use sudo to run commands which interact with the Docker daemon
# (see https://docs.docker.com/engine/install/linux-postinstall/):
sudo usermod -aG docker "$USER"
