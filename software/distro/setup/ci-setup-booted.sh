#!/bin/bash -eu
# This script runs setup steps which must be performed in a booted environment (e.g. a booted
# Raspberry Pi, virtual machine, or systemd-nspawn container).

# Determine the base path for sub-scripts

setup_scripts_root=$(dirname $(realpath $BASH_SOURCE))

# Get command-line args

hardware_type="$1" # should be either none, adafruithat, planktoscopehat, or segmenter-only

# Run sub-scripts

$setup_scripts_root/base-os/setup-booted.sh "$hardware_type"
