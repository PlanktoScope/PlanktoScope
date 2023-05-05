#!/bin/bash -euxo pipefail
# The localization configuration provides a set of defaults for internationalization and
# localization settings.

# Generate the en_US and en_DK UTF-8 locales for use. Note: refer to the contents of
# /usr/share/i18n/SUPPORTED for a list of locales which can be generated.
sudo bash -c 'cat > /etc/locale.gen' << EOT
en_US.UTF-8 UTF-8
en_DK.UTF-8 UTF-8
EOT
sudo dpkg-reconfigure --frontend=noninteractive locales

# Update the default locales so that the base-locale is en_US.UTF-8, while the date format is yyyy-mm-dd,
# units are metric, and paper sizes are international.
# FIXME: https://wiki.debian.org/Locale#Standard recommends that instead we should actually set the
# default locale to "None" - so that users who access the system over SSH can set their own locale
# using the LANG environment variable. However, the PlanktoScope's Node-RED frontend is probably
# relying on system commands using the default locale, so we still need to set a non-"None" locale
# until we clean up the PlanktoScope's Node-RED frontend to run command with a locale environment
# variable set, e.g. `LANG=en_DK.UTF-8 date`, or ultimately to run commands without relying on
# locales, e.g. using formatting strings to get a system date. Afterwards, we can just set the
# default locale to None using the command`sudo update-locale --reset`.
export LANG="en_US.UTF-8"
export LC_TIME="en_DK.UTF-8"
export LC_MEASUREMENT="en_DK.UTF-8"
export LC_PAPER="en_DK.UTF-8"
sudo update-locale LANG="$LANG" LC_TIME="$LC_TIME" LC_MEASUREMENT="$LC_MEASUREMENT" LC_PAPER="$LC_PAPER"

# Set the timezone to UTC
sudo timedatectl set-timezone UTC
