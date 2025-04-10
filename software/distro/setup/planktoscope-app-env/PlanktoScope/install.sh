#!/bin/bash -eux
# The PlanktoScope monorepo is used for running and iterating on software components

sudo cp -r "$repo_root" "$HOME/PlanktoScope"
sudo chown -R pi:pi "$HOME/PlanktoScope"
