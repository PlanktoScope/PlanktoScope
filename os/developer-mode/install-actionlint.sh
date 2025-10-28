#!/bin/bash -eux

wget https://github.com/rhysd/actionlint/releases/download/v1.7.8/actionlint_1.7.8_linux_arm64.tar.gz -P /tmp
cd /tmp && tar -xzf /tmp/actionlint_1.7.8_linux_arm64.tar.gz actionlint
sudo cp /tmp/actionlint /usr/local/bin/actionlint
