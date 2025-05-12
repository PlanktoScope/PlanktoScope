#!/bin/bash -eux
# Overclocking is supposed to improve the speed of the image segmentation process, though the exact
# decrease in battery time (or decrease in battery life when segmentation is not running) has not
# yet been rigorously measured and reported.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath "$BASH_SOURCE)

# Overvoltage to 6 and set clock speed to 2 GHz, for a V_core of 1.0125, a maximum allowable
# temperature of 72 deg C, a power draw of 11 Watt, and a performance increase of 33%.
file="/boot/firmware/config.txt"
sudo bash -c "cat \"$config_files_root$file.snippet\" >> \"$file\""
