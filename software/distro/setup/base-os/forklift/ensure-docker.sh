#!/bin/bash -eux
# This script does whatever is needed to ensure that the Docker daemon is running, even if the
# script is being run in an unbooted container where systemd is unavailable.

if ! [ -S /var/run/docker.sock ] &&
  ! sudo -E docker info &&
  ! sudo systemctl start docker.socket docker.service; then
  echo "Warning: couldn't start docker the easy way!"
  echo "Starting containerd daemon directly..."
  sudo /usr/bin/containerd &
  echo "Starting docker daemon directly..."
  sudo /usr/bin/dockerd &
  sleep 5
fi
if ! sudo docker image ls >/dev/null; then
  echo "Error: couldn't use docker client! Trying again in a few seconds..."
  sleep 5 # maybe this isn't needed?
  if ! sudo docker image ls >/dev/null; then
    echo "Error: couldn't use docker client!"
    exit 1
  fi
fi
