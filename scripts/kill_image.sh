#!/bin/bash    

#In order to kill an on going acquisition, type this command
#bash $HOME/PlanktonScope/scripts/kill_image.sh image.py in_path sample_project sample_id acq_id

path=$1

kill -9 `ps ax | grep "image.py" | head -1 | awk '{print $1}'`
kill -9 `ps ax | grep "image.py" | head -1 | awk '{print $1}'`

rm -r $path
