#!/bin/bash -eux

DISTRO_VERSION_ID="$(. /etc/os-release && echo "$VERSION_ID")"

# FIXME: remove this section entirely, to improve performance on bullseye.
# Refer to https://www.raspberrypi.com/documentation/computers/legacy_config_txt.html#gpu_mem
# for rationale. Note that we might need to first replace raspimjpeg with picamera2.
# The following command sets the GPU memory to 256:
if [ $DISTRO_VERSION_ID -ge 12 ]; then # Support Raspberry Pi OS 12 (bookworm)
  echo "GPU memory split cannot be changed on this platform."
else # Support Raspberry Pi OS 11 (bullseye)
  sudo raspi-config nonint do_memory_split 256
fi
