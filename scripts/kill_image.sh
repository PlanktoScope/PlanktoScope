#!/bin/bash    

#In order to kill an on going acquisition, type this command
#bash $HOME/PlanktonScope/scripts/kill_image.sh image.py sample_project sample_id acq_id

sample_project=$1
sample_id=$2
acq_id=$3

kill -9 `ps ax | grep "python3.7 image.py" | head -1 | awk '{print $1}'`

rm -r $HOME/PlanktonScope/acquisitions/$sample_project/$sample_id/$acq_id
