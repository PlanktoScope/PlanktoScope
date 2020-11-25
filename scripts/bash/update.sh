#!/bin/bash

cd /home/pi/PlanktonScope

git stash
git pull
git checkout stash@{0} -- config.json hardware.json 
