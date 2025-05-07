#!/bin/bash -eux
# Cockpit enables system administration from a web browser.

# Install cockpit
# Note: we need to adjust update-initramfs's behavior to make apt-get finish successfully; see
# https://github.com/PlanktoScope/PlanktoScope/pull/596 and
# https://github.com/RPi-Distro/repo/issues/382 for details.
grep -r MODULES /etc/initramfs-tools
sed -i 's~MODULES=dep~MODULES=most~' /etc/initramfs-tools/initramfs.conf
sudo -E apt-get install -y --no-install-recommends -o Dpkg::Progress-Fancy=0 \
	cockpit cockpit-networkmanager cockpit-storaged
sed -i 's~MODULES=most~MODULES=dep~' /etc/initramfs-tools/initramfs.conf
