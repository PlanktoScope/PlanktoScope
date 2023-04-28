#!/bin/bash

sudo killall -15 python3
sudo killall -15 raspimjpeg
sleep 10
sudo killall -9 python3
sudo killall -9 raspimjpeg
