#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Clear git repo - can be re-init with enable-developer-mode.sh
rm -rf $HOME/PlanktoScope/.git

# Clean up any unnecessary apt files
sudo apt-get autoremove -y
sudo apt-get clean -y

# Clean up any unnecessary pip, poetry, and npm files
pip3 cache purge || true
sudo rm -rf $HOME/.cache/pip
POETRY_VENV=$HOME/.local/share/pypoetry/venv
if [ -f $POETRY_VENV/bin/poetry ]; then
  BACKEND_CONTROLLER=$HOME/PlanktoScope/device-backend/control
  $POETRY_VENV/bin/poetry --no-interaction --directory $BACKEND_CONTROLLER cache clear _default_cache --all
  $POETRY_VENV/bin/poetry --no-interaction --directory $BACKEND_CONTROLLER cache clear piwheels --all
fi

# Remove history files
rm -f $HOME/.python_history
