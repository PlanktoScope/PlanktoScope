#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
distro_setup_files_root="$(dirname "$(dirname "$config_files_root")")"
repo_root="$(dirname "$(dirname "$(dirname "$distro_setup_files_root")")")"

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
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 \
  git python3-pip python3-venv

# Suppress keyring dialogs when setting up the PlanktoScope distro on a graphical desktop
# (see https://github.com/pypa/pip/issues/7883)
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

# Install Poetry
# Note: Because the poetry installation process (whether with pipx or the official installer) always
# selects the most recent version of the cryptography dependency, we must instead do a manual poetry
# installation to ensure that a wheel is available from piwheels for the cryptography dependency.
# We have had problems in the past with a version of that dependency not being available from
# piwheels.
POETRY_VENV=$HOME/.local/share/pypoetry/venv
mkdir -p "$POETRY_VENV"
python3 -m venv "$POETRY_VENV"
"$POETRY_VENV/bin/pip" install --upgrade --progress-bar off \
  pip==23.3.2 setuptools==68.2.2
"$POETRY_VENV/bin/pip" install --progress-bar off cryptography==41.0.5
"$POETRY_VENV/bin/pip" install --progress-bar off poetry==2.1.2

# Download device-backend monorepo
backend_version="$(cat "$config_files_root/backend-version")"
git clone "https://github.com/PlanktoScope/PlanktoScope.git" "$HOME/repo" --no-checkout --filter=blob:none
git -C "$HOME/repo" checkout --quiet "$backend_version"

# Historically device-backend lived in its own repository at https://github.com/PlanktoScope/device-backend
# and was cloned to $HOME/device-backend, it was later merged into the PlanktoScope monorepo
# we keep a bind mount until the transition is complete
mkdir -p $HOME/device-backend
sudo mount --bind $HOME/repo/device-backend $HOME/device-backend
echo "$HOME/repo/device-backend $HOME/device-backend none defaults,bind" | sudo tee -a /etc/fstab

# Set up the hardware controllers
# Upgrade python3-libcamera to solve an issue in Raspberry Pi OS bookworm-2024-11-19
# https://github.com/raspberrypi/picamera2/issues/1229#issuecomment-2772493538
# Once this fails in CI, it means the default version of python3-libcamera in
# Raspberry Pi OS has been updated. In which case this can be removed.
echo "If the next command fails, see comment in install.sh"
sudo -E apt-get install -y -o Dpkg::Progress-Fancy=0 --only-upgrade \
  python3-libcamera=0.4.0+rpt20250213-1
sudo -E apt-get install -y --no-install-recommends -o Dpkg::Progress-Fancy=0 \
  i2c-tools libopenjp2-7 python3-picamera2
"$POETRY_VENV/bin/poetry" --directory "$HOME/device-backend/control" install \
  --no-root --compile
file="/etc/systemd/system/planktoscope-org.device-backend.controller-adafruithat.service"
sudo cp "$config_files_root$file" "$file"
# or for the PlanktoScope HAT
file="/etc/systemd/system/planktoscope-org.device-backend.controller-planktoscopehat.service"
sudo cp "$config_files_root$file" "$file"

# Select the enabled hardware controller
mkdir -p "$HOME/PlanktoScope"
sudo systemctl enable "planktoscope-org.device-backend.controller-$hardware_type.service"
cp "$HOME/device-backend/default-configs/$default_config.hardware.json" \
  "$HOME/PlanktoScope/hardware.json"
