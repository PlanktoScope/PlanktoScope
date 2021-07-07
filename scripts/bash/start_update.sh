#!/bin/bash
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