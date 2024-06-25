#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Determine the base path for copied files
config_files_root=$(dirname $(realpath $BASH_SOURCE))
distro_setup_files_root=$(dirname $(dirname $config_files_root))
repo_root=$(dirname $(dirname $(dirname $distro_setup_files_root)))

# Get command-line args
hardware_type="$1" # should be either adafruithat, planktoscopehat, or fairscope-latest
default_config="$hardware_type-latest"
case "$hardware_type" in
  "fairscope-latest")
    hardware_type="planktoscopehat"
    default_config="fairscope-latest"
    ;;
esac

## Install basic Python tooling
sudo apt-get install -y -o Dpkg::Progress-Fancy=0 \
  git python3-pip python3-venv

# Suppress keyring dialogs when setting up the PlanktoScope distro on a graphical desktop
# (see https://github.com/pypa/pip/issues/7883)
PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

# Install Poetry
# Note: Because the poetry installation process (whether with pipx or the official installer) always
# selects the most recent version of the cryptography dependency, we must instead do a manual poetry
# installation to ensure that a wheel is available from piwheels for the cryptography dependency.
# We have had problems in the past with a version of that dependency not being available from
# piwheels.
POETRY_VENV=$HOME/.local/share/pypoetry/venv
mkdir -p $POETRY_VENV
python3 -m venv $POETRY_VENV
$POETRY_VENV/bin/pip install --upgrade --progress-bar off \
  pip==23.3.2 setuptools==68.2.2
$POETRY_VENV/bin/pip install --progress-bar off cryptography==41.0.5
$POETRY_VENV/bin/pip install --progress-bar off poetry==1.7.1

# Download device-backend monorepo
backend_repo="github.com/PlanktoScope/device-backend"
backend_version="v2024.0.0-beta.1" # this should be either a version tag, branch name, or commit hash
git clone "https://$backend_repo" $HOME/device-backend --no-checkout --filter=blob:none
git -C $HOME/device-backend checkout --quiet $backend_version

# Set up the hardware controllers
# Note(ethanjli): we use picamera2 from the system for compatibility, and because dependencies are
# annoying to manage on armv7. Once we migrate to RPi OS 12 (bookworm), let's try again to just
# install it via poetry.
sudo apt-get install -y --no-install-recommends -o Dpkg::Progress-Fancy=0 \
  i2c-tools libopenjp2-7 python3-picamera2
$POETRY_VENV/bin/poetry --directory $HOME/device-backend/control config \
  virtualenvs.options.system-site-packages true --local
$POETRY_VENV/bin/poetry --directory $HOME/device-backend/control install \
  --no-root --compile
file="/etc/systemd/system/planktoscope-org.device-backend.controller-adafruithat.service"
sudo cp "$config_files_root$file" "$file"
# or for the PlanktoScope HAT
file="/etc/systemd/system/planktoscope-org.device-backend.controller-planktoscopehat.service"
sudo cp "$config_files_root$file" "$file"
# FIXME: make this directory in the main.py file
sudo -E mkdir -p $HOME/data/img
sudo -E mkdir -p $HOME/device-backend-logs/control

# Select the enabled hardware controller
mkdir -p $HOME/PlanktoScope
sudo systemctl enable "planktoscope-org.device-backend.controller-$hardware_type.service"
cp "$HOME/device-backend/default-configs/$default_config.hardware.json" \
  $HOME/PlanktoScope/hardware.json

# Copy required dependencies with hard-coded paths in the hardware controller
# TODO: get rid of this when we remove raspimjpeg
mkdir -p $HOME/PlanktoScope/scripts
directory="scripts/raspimjpeg"
cp -r "$repo_root/$directory" $HOME/PlanktoScope/$directory
