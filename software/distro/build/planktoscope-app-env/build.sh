#!/bin/bash -eu
# The PlanktoScope application environment is the set of all software applications
# and configurations specific to the PlanktoScope, which builds on the base operating
# system.
# In the future, hopefully this will be reduced to the deployment of a set of
# Pallet packages.

# Determine the base path for sub-scripts

build_scripts_root = $(dirname $(realpath $BASH_SOURCE))

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

description="install MQTT broker"
report_starting "$description"
if $build_scripts_root/mqtt-broker/install.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up Python backend"
report_starting "$description"
if $build_scripts_root/python-backend/install.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="configure GPIO stepper initialization"
report_starting "$description"
if $build_scripts_root/gpio-stepper-init/config.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up Node-RED frontend"
report_starting "$description"
if $build_scripts_root/node-red-frontend/install.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up GPS and clock driver"
report_starting "$description"
if $build_scripts_root/gps/install.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="configure networking"
report_starting "$description"
if $build_scripts_root/networking/config.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="remove unnecessary artifacts"
report_starting "$description"
if $build_scripts_root/cleanup/clean.sh ; then
  report_finished "$description"
else
  panic "$description"
fi
