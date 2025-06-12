#!/bin/bash -eux
# Cleanup removes unnecessary files from the operating system for a smaller and more secure disk image.

# Clean up any unnecessary apt files
sudo apt-get autoremove -y
sudo apt-get clean -y

# Clean up any unnecessary pip, poetry, and npm files
pip3 cache purge || true
rm -rf $HOME/.cache/pip
poetry cache clear --no-interaction --all .

# Remove history files
rm -f $HOME/.python_history
rm -f $HOME/.bash_history
