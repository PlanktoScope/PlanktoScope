#!/bin/bash -eux

build_scripts_root=$(dirname "$(realpath "$BASH_SOURCE")")

export PATH="$HOME/.local/bin:$PATH"
export LANG="en_US.UTF-8"

# The PlanktoScope monorepo is used for running and iterating on software components
# https://github.com/PlanktoScope/planktoscope
sudo cp -r "$build_scripts_root"/.. "$HOME/PlanktoScope"
sudo chown -R "$USER:$USER" "$HOME/PlanktoScope"

./"$HOME"/PlanktoScope/os/developer-mode/install-just.sh

just --justfile "$HOME"/PlanktoScope/justfile base
just --justfile "$HOME"/PlanktoScope/justfile setup
just --justfile "$HOME"/PlanktoScope/os/justfile cleanup
