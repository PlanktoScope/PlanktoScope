#!/bin/bash -eux

# https://systemd.io/BUILDING_IMAGES/
sudo rm -f /var/lib/systemd/random-seed
sudo rm -f /var/lib/systemd/credential.secret

sudo rm -f /etc/ssh/ssh_host_*_key*

poetry cache clear --no-interaction --all .
npm cache clean --force
rm -rf "$HOME"/.cache
mkdir "$HOME"/.cache

rm -f "$HOME"/.python_history
rm -f "$HOME"/.bash_history
