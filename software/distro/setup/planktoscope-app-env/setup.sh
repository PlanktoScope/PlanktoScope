#!/bin/bash -eu
# The PlanktoScope application environment is the set of all software applications
# and configurations specific to the PlanktoScope, which builds on the base operating
# system.
# In the future, hopefully this will be reduced to the deployment of a set of
# Pallet packages.

# Determine the base path for sub-scripts

build_scripts_root=$(dirname "$(realpath "$BASH_SOURCE")")

# Get command-line args

hardware_type="$1" # should be either adafruithat, planktoscopehat, fairscope-latest

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

description="set up /home/pi/PlanktoScope"
report_starting "$description"
if "$build_scripts_root/PlanktoScope/install.sh"; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up Node-RED frontend"
report_starting "$description"
if "$build_scripts_root/node-red-frontend/install.sh" "$hardware_type"; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up Python hardware controller"
report_starting "$description"
if "$build_scripts_root/python-hardware-controller/install.sh" "$hardware_type"; then
  report_finished "$description"
else
  panic "$description"
fi

if [ "$hardware_type" = "adafruithat" ]; then
  description="set up GPS and clock driver"
  report_starting "$description"
  if "$build_scripts_root/gps/install.sh"; then
    report_finished "$description"
  else
    panic "$description"
  fi
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
