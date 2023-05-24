#!/bin/bash
# Copyright (C) 2021 Romain Bazile
#
# This file is part of the PlanktoScope software.
#
# PlanktoScope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PlanktoScope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PlanktoScope.  If not, see <http://www.gnu.org/licenses/>.

log="echo -e"

CURRENT_BRANCH=$(git --git-dir=/home/pi/PlanktoScope/.git rev-parse --abbrev-ref HEAD)
REMOTE_BRANCHES=$(git --git-dir=/home/pi/PlanktoScope/.git branch --remotes --list | awk '/HEAD/{next;} split($1, a, "/") {print a[2]}')
if [[ $# == 1 ]]; then
    if [[ $REMOTE_BRANCHES =~ (^|[[:space:]])$1($|[[:space:]]) ]]; then
        BRANCH="$1"
    else
        BRANCH="$CURRENT_BRANCH"
    fi
else
    BRANCH="$CURRENT_BRANCH"
fi
${log} "Updating the installer script from $BRANCH"
curl "https://raw.githubusercontent.com/PlanktonPlanet/PlanktoScope/$BRANCH/scripts/bash/update.sh" > /tmp/update.sh
chmod +x /tmp/update.sh
exec /tmp/update.sh "$BRANCH"
