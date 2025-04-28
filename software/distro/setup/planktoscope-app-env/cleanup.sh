#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Clear git repo - can be re-init with enable-developer-mode.sh
rm -rf $HOME/PlanktoScope/.git

# Clean up any unnecessary apt files
sudo apt-get autoremove -y
sudo apt-get clean -y

# Clean up any unnecessary pip, poetry, and npm files
pip3 cache purge || true
rm -rf $HOME/.cache/pip
poetry cache clear --all .

# Remove history files
rm -f $HOME/.python_history
rm -f $HOME/.bash_history
