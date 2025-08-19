#!/bin/bash -eux

# TODO: On Debian 13 we can use the just package from Debian repositories

wget https://github.com/casey/just/releases/download/1.42.4/just-1.42.4-arm-unknown-linux-musleabihf.tar.gz -P /tmp
cd /tmp && tar -xzf /tmp/just-1.42.4-arm-unknown-linux-musleabihf.tar.gz just
sudo cp /tmp/just /usr/bin/just
