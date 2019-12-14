#!/bin/bash    

#In order to kill an on going acquisition, type this command
#bash $HOME/PlanktonScope/scripts/kill_image.sh image.py sample_project sample_id acq_id

in_path=$1
sample_project=$2
sample_id=$3
acq_id=$4

kill -9 `ps ax | grep "image.py" | head -1 | awk '{print $1}'`

rm -r $in_path/$sample_project/$sample_id/$acq_id
bash $HOME/RPi_Cam_Web_Interface/start.sh

