#!/bin/bash -eux
# The PlanktoScope monorepo is used for running and iterating on software components

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
distro_setup_files_root="$(dirname "$(dirname "$config_files_root")")"
repo_root="$(dirname "$(dirname "$(dirname "$distro_setup_files_root")")")"

sudo cp -r "$repo_root" "$HOME/PlanktoScope"
sudo chown -R pi:pi "$HOME/PlanktoScope"
