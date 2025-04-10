#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

cp -r "$repo_root" $HOME/PlanktoScope
sudo chown -R pi:pi $HOME/PlanktoScope