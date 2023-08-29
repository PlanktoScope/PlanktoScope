#!/bin/bash -eux
# The platform hardware specific to the PlanktoScope app environment consists of an RTC module.

config_files_root=$(dirname $(realpath $BASH_SOURCE))

# Enable kernel drivers for the PlanktoScope
file="/boot/config.txt"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""
