#!/bin/bash -eux

# Determine the base path for sub-scripts

build_scripts_root=$(dirname "$(realpath "$BASH_SOURCE")")

# Set up pretty error printing

red_fg=31
blue_fg=34
bold=1

subscript_fmt="\e[${bold};${blue_fg}m"
error_fmt="\e[${bold};${red_fg}m"
reset_fmt='\e[0m'

function report_starting {
  echo
  echo -e "${subscript_fmt}Starting: ${1}...${reset_fmt}"
}
function report_finished {
  echo -e "${subscript_fmt}Finished: ${1}!${reset_fmt}"
}
function panic {
  echo -e "${error_fmt}Error: couldn't ${1}${reset_fmt}"
  exit 1
}
# Run sub-scripts

echo -e "${subscript_fmt}Setting up full operating system...${reset_fmt}"

export PATH="$HOME/.local/bin:$PATH"
export LANG="en_US.UTF-8"

sudo apt-get update -y -o Dpkg::Progress-Fancy=0 -o DPkg::Lock::Timeout=60

description="install base tools"
report_starting "$description"
if "$build_scripts_root"/tools/install.sh; then
  report_finished "$description"
else
  panic "$description"
fi

description="configure system locales"
report_starting "$description"
if "$build_scripts_root"/localization/config.sh; then
  report_finished "$description"
else
  panic "$description"
fi

description="configure networking"
report_starting "$description"
if "$build_scripts_root"/networking/install.sh; then
  report_finished "$description"
else
  panic "$description"
fi

description="configure Raspberry Pi-specific hardware"
report_starting "$description"
if "$build_scripts_root"/platform-hardware/config.sh; then
  report_finished "$description"
else
  panic "$description"
fi

# Note: we must install Docker before we perform Forklift container image loading (which requires
# either Docker or containerd, which is installed by Docker).
description="install Docker"
report_starting "$description"
if "$build_scripts_root"/docker/install.sh; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up Forklift"
report_starting "$description"
if "$build_scripts_root"/forklift/install.sh; then
  report_finished "$description"
else
  panic "$description"
fi

description="install Cockpit"
report_starting "$description"
if "$build_scripts_root"/cockpit/install.sh; then
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

description="enable CPU overclocking"
report_starting "$description"
if "$build_scripts_root/overclocking/config.sh"; then
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

"$setup_scripts_root"/cleanup.sh
