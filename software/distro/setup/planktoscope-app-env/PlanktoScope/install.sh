#!/bin/bash -eux
# The Python backend provides a network API abstraction over hardware devices, as well as domain
# logic for operating the PlanktoScope hardware.

# Determine the base path for copied files
config_files_root="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# Download monorepo
backend_version="$(cat "$config_files_root/backend-version")"
git clone "https://github.com/PlanktoScope/PlanktoScope.git" "$HOME/repo" --no-checkout --filter=blob:none
git -C "$HOME/repo" checkout --quiet "$backend_version"
