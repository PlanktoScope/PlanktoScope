#!/bin/bash -eu
# The software distro is the complete, finished, fully-function operating system
# for the PlanktoScope. The resulting image can be flashed to an SD card, inserted
# into a PlanktoScope, and booted up to make the PlanktoScope fully operational.
# Note: currently the setup script assumes that it will be installed to /home/pi
# for the `pi` user.

# Determine the base path for sub-scripts

setup_scripts_root=$(dirname $(realpath $BASH_SOURCE))

# Get command-line args

hardware_type="$1" # should be either none, adafruithat, planktoscopehat, or segmenter-only

# Run sub-scripts

$setup_scripts_root/base-os/setup-in-vm.sh "$hardware_type"
