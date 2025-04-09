#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

USER_CACHE_DIR="$(systemd-path user-state-cache)"

# apt
sudo apt-get autoremove -y
sudo apt-get clean -y

# pip
pip3 cache purge || true
rm -rf ${USER_CACHE_DIR}/pip

# poetry
# https://github.com/python-poetry/poetry/issues/8156#issuecomment-1620770507
poetry cache clear --all . || true
rm -rf ${USER_CACHE_DIR}/pypoetry

# history files
rm -f $HOME/.python_history
rm -F $HOME/.bash_history
