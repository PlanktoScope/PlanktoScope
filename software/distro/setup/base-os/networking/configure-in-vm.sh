#!/bin/bash -eux

# Set the wifi country
if [ -f /dev/rfkill ]; then
  sudo rfkill unblock wifi
else
  echo "Warning: rfkill is not available, so we can't unblock the Wi-Fi interface!"
fi
