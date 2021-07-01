#!/bin/bash
log="echo -e"

${log} "Updating the installer script from $BRANCH"

REMOTE_BRANCHES=$(git --git-dir=/home/pi/PlanktoScope/.git branch --remotes --list | awk '/HEAD/{next;} split($1, a, "/") {print a[2]}')
if [[ $# == 1 ]]; then
    if [[ $REMOTE_BRANCHES =~ (^| )$1($| ) ]]; then
        BRANCH=$1
    else
        BRANCH="master"
    fi
else
    BRANCH="master"
fi

curl "https://raw.githubusercontent.com/PlanktonPlanet/PlanktoScope/$BRANCH/scripts/bash/update.sh" > /tmp/update.sh

exec /tmp/update.sh "$BRANCH"
