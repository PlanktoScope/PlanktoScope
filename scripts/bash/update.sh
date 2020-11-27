#!/bin/bash
log="logger -t update.sh -s "

${log} "Updating the main repository"
cd /home/pi/PlanktonScope

git stash
git pull
git checkout stash@{0} -- config.json hardware.json 
${log} "Done!"