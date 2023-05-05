#!/bin/bash -euxo pipefail
# The base OS tools enable basic operation of the OS, and provide generalized mechanisms for
# bootstrapping further software (e.g. user applications) to be installed afterwards.

# Install some tools for a nicer command-line experience over ssh
sudo apt-get update -y
sudo apt-get install -y vim byobu git

# Install Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# The following command will fail with a post-install error if the system installed kernel updates
# via apt upgrade but was not rebooted before installing docker-ce; however, even if this error
# is reported, docker will work after reboot.
# Refer to https://www.reddit.com/r/raspberry_pi/comments/zblky6/comment/iytpp4g/ for details.
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
