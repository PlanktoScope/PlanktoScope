#!/bin/bash -eux

build_scripts_root=$(dirname "$(realpath "$BASH_SOURCE")")

export PATH="$HOME/.local/bin:$PATH"
export LANG="en_US.UTF-8"

# The PlanktoScope monorepo is used for running and iterating on software components
# https://github.com/PlanktoScope/planktoscope
sudo cp -r "$build_scripts_root"/.. "$HOME/PlanktoScope"
sudo chown -R "$USER:$USER" "$HOME/PlanktoScope"

./"$HOME"/PlanktoScope/os/developer-mode/install-just.sh

<<<<<<< HEAD
description="configure Raspberry Pi-specific hardware"
report_starting "$description"
if "$build_scripts_root"/platform-hardware/config.sh; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up /home/pi/PlanktoScope"
report_starting "$description"
if "$build_scripts_root/PlanktoScope/install.sh"; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up Node-RED frontend"
report_starting "$description"
if "$build_scripts_root/node-red-frontend/install.sh"; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up Python hardware controller"
report_starting "$description"
if "$build_scripts_root/python-hardware-controller/install.sh"; then
  report_finished "$description"
else
  panic "$description"
fi

description="update and configure bootloader"
report_starting "$description"
if "$build_scripts_root/bootloader/install.sh"; then
  report_finished "$description"
else
  panic "$description"
fi

description="install just"
report_starting "$description"
if "$build_scripts_root/developer-mode/install-just.sh"; then
  report_finished "$description"
else
  panic "$description"
fi

description="run just scripts"
report_starting "$description"
just --justfile "$build_scripts_root"/justfile setup

"$build_scripts_root"/cleanup.sh
=======
just --justfile "$HOME"/PlanktoScope/justfile base
just --justfile "$HOME"/PlanktoScope/justfile setup
just --justfile "$HOME"/PlanktoScope/os/justfile cleanup
>>>>>>> main
