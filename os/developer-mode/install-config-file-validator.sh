#!/bin/bash -eux

# dasel is a good alternative available in deb repositories but does not support ini

wget https://github.com/Boeing/config-file-validator/releases/download/v1.8.1/validator-v1.8.1-linux-arm64.tar.gz -P /tmp
cd /tmp && tar -xzf /tmp/validator-v1.8.1-linux-arm64.tar.gz validator
sudo cp /tmp/validator /usr/local/bin/validator
