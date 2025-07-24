#!/bin/bash -eux

build_scripts_root=$(dirname "$(realpath "$BASH_SOURCE")")

export PATH="$HOME/.local/bin:$PATH"
export LANG="en_US.UTF-8"

# The PlanktoScope monorepo is used for running and iterating on software components
# https://github.com/PlanktoScope/planktoscope
sudo cp -r "$repo_root" "$HOME/PlanktoScope"
sudo chown -R pi:pi "$HOME/PlanktoScope"

sudo chown -R "$USER" "$build_scripts_root"/..

just --justfile "$build_scripts_root"/../justfile base
just --justfile "$build_scripts_root"/../justfile setup

just cleanup
