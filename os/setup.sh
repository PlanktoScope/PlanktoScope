#!/bin/bash -eux

export PATH="$HOME/.local/bin:$PATH"
export LANG="en_US.UTF-8"

# The PlanktoScope monorepo is used for running and iterating on software components
# https://github.com/PlanktoScope/planktoscope
sudo chown -R "$USER:$USER" ..
sudo cp -r .. "$HOME/PlanktoScope"

just --justfile ../justfile base
just --justfile ../justfile setup

just cleanup
