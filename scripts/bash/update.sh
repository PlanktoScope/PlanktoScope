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

${log} "Updating the main repository to branch $BRANCH"

function restart(){
    sudo nginx -t && sudo systemctl reload nginx
    sudo systemctl restart nodered.service
}

function update(){
    cd /home/pi/PlanktoScope || { echo "/home/pi/PlanktoScope does not exist"; exit 1; }
    sudo killall -15 raspimjpeg
    sudo killall -15 python3
    git stash
    # TODO detect branch change and use git pull on same branch and checkout on diff branch
    if [[ "$CURRENT_BRANCH" == "$BRANCH" ]]; then
        git pull
    else
        git checkout --force "$BRANCH"
    fi
    git checkout stash@'{0}' -- config.json hardware.json
    # TODO we need to change this to drop stash@{1} if changes made to the flow are to be restored by the user
    git stash drop
}

function special_before(){
    cd /home/pi/.node-red || { echo "/home/pi/.node-red does not exist"; exit 1; }
    sudo rpi-eeprom-update -a
    ${log} "Nothing else special to do before updating!"
}

function special_after(){
    cd /home/pi/.node-red || { echo "/home/pi/.node-red does not exist"; exit 1; }
    #node_modules/copy-dependencies/index.js projects/PlanktoScope ./
    # updating and installing now whatever module has been added to package.json
    #npm update
    #pip3 install -U -r /home/pi/PlanktoScope/requirements.txt
    ${log} "Nothing else special to do after updating!"
}

echo -e "\n\n\nUpdate on $(date)\n\n" >> /home/pi/update.log
cd /home/pi/PlanktoScope || { echo "/home/pi/PlanktoScope does not exist"; exit 1; }
remote=$(git ls-remote -h origin "$BRANCH" | awk '{print $1}')
local=$(git rev-parse HEAD)
if [[ "$local" == "$remote" ]]; then
    ${log} "Nothing to do!"
else
    ${log} "Local and Remote are different, we have to update, starting now... Please Wait."
    special_before &>> /home/pi/update.log
    ${log} "Everything is ready, doing the actual update now!"
    update &>> /home/pi/update.log
    #special_after &>> /home/pi/update.log
    ${log} "Update is complete, let's restart now."
    restart &>> /home/pi/update.log
fi
${log} "Update done!"