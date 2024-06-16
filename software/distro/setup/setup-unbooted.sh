#!/bin/bash -eu
# This script runs setup steps which can be performed in an unbooted environment on an OS image
# which is mounted as the root filesystem (e.g. in an unbooted systemd-nspawn container or in a
# pimod script).

# Determine the base path for sub-scripts

setup_scripts_root=$(dirname $(realpath $BASH_SOURCE))

# Get command-line args

hardware_type="$1" # should be either none, adafruithat, planktoscopehat, fairscope-latest, or segmenter-only

# Set up pretty error printing

red_fg=31
blue_fg=34
magenta_fg=35
bold=1

script_fmt="\e[${bold};${magenta_fg}m"
error_fmt="\e[${bold};${red_fg}m"
reset_fmt='\e[0m'

function report_starting {
  echo
  echo -e "${script_fmt}Starting: ${1}...${reset_fmt}"
}
function report_finished {
  echo
  echo -e "${script_fmt}Finished: ${1}!${reset_fmt}"
}
function panic {
  echo -e "${error_fmt}Error: couldn't ${1}${reset_fmt}"
  exit 1
}

# Run sub-scripts

echo -e "${script_fmt}Setting up full operating system...${reset_fmt}"

description="set up base operating system"
report_starting "$description"
if $setup_scripts_root/base-os/setup-unbooted.sh ; then
  report_finished "$description"
  source $setup_scripts_root/base-os/export-env.sh
else
  panic "$description"
fi

if [ $hardware_type = "none" ]; then
  echo "Warning: skipping PlanktoScope-specific setup because hardware type was specified as: $hardware_type"
else
  description="set up PlanktoScope application environment"
  report_starting "$description"
  if $setup_scripts_root/planktoscope-app-env/setup.sh "$hardware_type" ; then
    report_finished "$description"
    source $setup_scripts_root/planktoscope-app-env/export-env.sh
  else
    panic "$description"
  fi
fi
