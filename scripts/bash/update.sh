#!/bin/bash
log="logger -t update.sh -s "

if [[ $# == 1 ]]; then
    BRANCH=$1
else
    BRANCH="master"
fi

${log} "Updating the main repository to branch $BRANCH"

function restart(){
    sudo nginx -t && sudo systemctl reload nginx
    sudo systemctl restart nodered.service
}

function update(){
    cd /home/pi/PlanktonScope || { echo "/home/pi/PlanktonScope does not exist"; exit 1; }
    sudo killall -15 raspimjpeg
    sudo killall -15 python3
    git stash
    git merge
    git checkout stash@'{0}' -- config.json hardware.json
    # TODO we need to change this to drop stash@{1} if changes made to the flow are to be restored by the user
    git stash drop
}

function special_before(){
    cd /home/pi/.node-red || { echo "/home/pi/.node-red does not exist"; exit 1; }
    npm install copy-dependencies
    pip3 install --update adafruit-blinka adafruit-platformdetect loguru Pillow pyserial smbus2 matplotlib morphocut adafruit-circuitpython-motor adafruit-circuitpython-motorkit adafruit-circuitpython-pca9685 numpy paho-mqtt
    ${log} "Nothing else special to do before updating!"
}

function special_after(){
    cd /home/pi/.node-red || { echo "/home/pi/.node-red does not exist"; exit 1; }
    node_modules/copy-dependencies/index.js projects/PlanktonScope ./
    # updating and installing now whatever module has been added to package.json
    npm update
    sudo pip3 install -U -r /home/pi/PlanktonScope/requirements.txt
    ${log} "Nothing else special to do after updating!"
}


cd /home/pi/PlanktonScope || { echo "/home/pi/PlanktonScope does not exist"; exit 1; }
remote=$(git ls-remote -h origin $BRANCH | awk '{print $1}')
local=$(git rev-parse HEAD)
if [[ "$local" == "$remote" ]]; then
    ${log} "nothing to do!"
else
    ${log} "Local and Remote are different, we have to update!"
    git fetch
    UPDATE=$(git diff --numstat origin/$BRANCH scripts/bash/update.sh | awk '/update.sh/ {print $NF}')
    if [[ -n "${UPDATE}" ]]; then
        # Update the file and restart the script
        git checkout origin/$BRANCH scripts/bash/update.sh
        exec scripts/bash/update.sh $BRANCH
    fi
    special_before
    update
    special_after
    restart
    ${log} "Done!"
fi