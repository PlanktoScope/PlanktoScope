#!/bin/bash
log="echo -e"

REMOTE_BRANCHES=$(git --git-dir=/home/pi/PlanktonScope/.git branch --remotes --list | awk '/HEAD/{next;} split($1, a, "/") {print a[2]}')
if [[ $# == 1 ]]; then
    if [[ $REMOTE_BRANCHES =~ (^| )$1($| ) ]]; then
        BRANCH=$1
    else
        BRANCH="master"
    fi
else
    BRANCH="master"
fi

${log} "Updating the main repository to branch $BRANCH"

function auto_update(){
    git fetch
    NEWVERSION=$(git diff --numstat origin/$BRANCH scripts/bash/update.sh | awk '/update.sh/ {print $NF}')
    if [[ -n "${NEWVERSION}" ]]; then
        ${log} "Updating the update script first"
        # Update the file and restart the script
        git checkout origin/$BRANCH scripts/bash/update.sh
        exec scripts/bash/update.sh $BRANCH
    fi
}

function restart(){
    sudo nginx -t && sudo systemctl reload nginx
    sudo systemctl restart nodered.service
}

function update(){
    cd /home/pi/PlanktonScope || { echo "/home/pi/PlanktonScope does not exist"; exit 1; }
    sudo killall -15 raspimjpeg
    sudo killall -15 python3
    git stash
    # TODO detect branch change and use git pull on same branch and checkout on diff branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$CURRENT_BRANCH" == "$BRANCH" ]]; then
        git pull
    else
        git checkout --force $BRANCH
    fi
    git checkout stash@'{0}' -- config.json hardware.json
    # TODO we need to change this to drop stash@{1} if changes made to the flow are to be restored by the user
    git stash drop
}

function special_before(){
    cd /home/pi/.node-red || { echo "/home/pi/.node-red does not exist"; exit 1; }
    npm install copy-dependencies
    pip3 install --upgrade adafruit-blinka adafruit-platformdetect loguru Pillow pyserial smbus2 matplotlib morphocut adafruit-circuitpython-motor adafruit-circuitpython-motorkit adafruit-circuitpython-pca9685 numpy paho-mqtt
    ${log} "Nothing else special to do before updating!"
}

function special_after(){
    cd /home/pi/.node-red || { echo "/home/pi/.node-red does not exist"; exit 1; }
    node_modules/copy-dependencies/index.js projects/PlanktonScope ./
    # updating and installing now whatever module has been added to package.json
    npm update
    sudo pip3 install -U -r /home/pi/PlanktonScope/requirements.txt
    python3 -m pip install -U scikit-image
    ${log} "Nothing else special to do after updating!"
}

echo -e "Update on $(date)\n\n\n\n" >> /home/pi/update.log
cd /home/pi/PlanktonScope || { echo "/home/pi/PlanktonScope does not exist"; exit 1; }
remote=$(git ls-remote -h origin $BRANCH | awk '{print $1}')
local=$(git rev-parse HEAD)
if [[ "$local" == "$remote" ]]; then
    ${log} "Nothing to do!"
else
    ${log} "Local and Remote are different, we have to update, starting now... Please Wait."
    auto_update &>> /home/pi/update.log
    special_before &>> /home/pi/update.log
    ${log} "Everything is ready, doing the update now!"
    update &>> /home/pi/update.log
    special_after &>> /home/pi/update.log
    ${log} "Update is complete, let's restart now."
    restart &>> /home/pi/update.log
fi
${log} "Update done!"