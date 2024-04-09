#!/bin/bash -eu
# The base operating system is a clean, minimal, and roughly generic base environment
# which is not too specific to the PlanktoScope, and which could maybe be repurposed
# for other projects.
# In the future, hopefully this will be a minimal set of software installations
# and configurations sufficient to bootstrap all higher layers within Docker
# containers.

# Determine the base path for sub-scripts

build_scripts_root=$(dirname $(realpath $BASH_SOURCE))

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

description="install base tools"
report_starting "$description"
if $build_scripts_root/tools/install.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="configure system locales"
report_starting "$description"
if $build_scripts_root/localization/config.sh ; then
  source $build_scripts_root/localization/export-env.sh
  report_finished "$description"
else
  panic "$description"
fi

description="configure Raspberry Pi-specific hardware"
report_starting "$description"
if $build_scripts_root/platform-hardware/config.sh ; then
  report_finished "$description"
else
  panic "$description"
fi

description="set up OS configuration with Forklift"
report_starting "$description"
if $build_scripts_root/forklift/install.sh ; then
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
