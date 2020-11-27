#!/bin/bash
log="logger -t update.sh -s "

${log} "Updating the main repository"
cd /home/pi/PlanktonScope

echo "Update output:\n"
sudo killall -15 raspimjpeg
sudo killall -15 python3
git stash
git pull
git checkout stash@{0} -- config.json hardware.json
git stash drop
sudo systemctl restart nodered.service
${log} "Done!"