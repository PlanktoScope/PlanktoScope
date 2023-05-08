#!/bin/bash
# This script was adapted (with various modifications and modernizations) from a script from
# RaspberryConnect.com

# You may share this script on the condition a reference to RaspberryConnect.com
# must be included in copies or derivatives of this script.

# When an external wifi network is available, connect to it; otherwise, make a new isolated wifi
# network; currently there is no support for bridging the ethernet or wifi networks (which would
# enable sharing internet access).
# Works at startup or with a separate timer or manually without a reboot.

wifi_dev="wlan0" # device name to use; by default wlan0 is the on-board wifi chip on the RPi4

# Determine the SSIDs of the wifi networks the RPi is configured to use:
# FIXME: can we simplify these commands?
wpa_ssid=$(grep -e '^ *ssid="' /etc/wpa_supplicant/wpa_supplicant.conf | \
  awk -F'ssid=' '{ print $2 }' | sed 's/\r//g' | \
  awk 'BEGIN{ORS=","} {print}' | sed 's/\"//g' | sed 's/,$//')
IFS="," read -r -a ssids <<<"$wpa_ssid"

start_isolated_wlan() {
  echo "Starting isolated wifi network..."
  ip link set dev "$wifi_dev" down
  ip address add 192.168.4.1/24 broadcast + dev "$wifi_dev"
  ip link set dev "$wifi_dev" up
  dhcpcd --release "$wifi_dev" >/dev/null 2>&1
  systemctl start hostapd
}

stop_isolated_wlan() {
  echo "Stopping isolated wifi network..."
  ip link set dev "$wifi_dev" down
  systemctl stop hostapd
  ip addr flush dev "$wifi_dev"
  ip link set dev "$wifi_dev" up
  dhcpcd --rebind "$wifi_dev" >/dev/null 2>&1
}

fallback_if_unusable_wifi() {
  echo "Checking whether external wifi network is usable..."
  attempt=0
  max_attempts=10
  while : ; do
    if ((attempt >= max_attempts)); then
      echo "Couldn't reach the internet after $max_attempts attempts, giving up!"
      break
    fi

    if ping -c 1 -W 2 google.com | grep '1 received' >/dev/null 2>&1; then
      echo "Successfully pinged google.com!"
      return 0
    fi
    echo "Not yet able to ping google.com (attempt $attempt of $max_attempts)!"
    if ! ping -c 1 -W 2 1.1.1.1 | grep '1 received' >/dev/null 2>&1; then
      echo "Not yet able to ping Cloudflare DNS at 1.1.1.1, either!"
      if ! wpa_cli -i "$wifi_dev" status | grep 'ip_address' >/dev/null 2>&1; then
        echo "No IP address assigned to $wifi_dev yet, either!"
        sleep 2
      fi
    fi
    attempt=$((attempt + 1))
  done
  echo "Failed to connect to external wifi network! Falling back to isolated wifi network..."
  wpa_cli terminate "$wifi_dev" >/dev/null 2>&1
  start_isolated_wlan
}

initialize_system_services() {
  # hostapd may be masked after system updates. This fixes any drift.
  # Ensure that hostapd is unmasked and disabled
  if systemctl -all list-unit-files hostapd.service | grep "hostapd.service masked" >/dev/null 2>&1; then
    systemctl unmask hostapd.service >/dev/null 2>&1
  fi
  if systemctl -all list-unit-files hostapd.service | grep "hostapd.service enabled" >/dev/null 2>&1; then
    systemctl disable hostapd.service >/dev/null 2>&1
    systemctl stop hostapd >/dev/null 2>&1
  fi
  # Ensure that dnsmasq is unmasked
  if systemctl -all list-unit-files dnsmasq.service | grep "dnsmasq.service masked" >/dev/null 2>&1; then
    systemctl unmask dnsmasq >/dev/null 2>&1
  fi
}

find_ssid() {
  # Check to see what SSIDs and MAC addresses are in range
  ssid_status="unavailable" # FIXME: use a bool instead

  if [ ${#ssids[@]} -eq 0 ]; then
    echo "No SSIDs were specified in wpa_supplicant config, skipping scan of wifi networks!"
    return 0
  fi

  detected_ssid=""
  attempt=0
  max_attempts=5
  while : ; do # wait for wifi if busy
    if ((attempt >= max_attempts)); then
      echo "Couldn't scan for networks after $max_attempts attempts, giving up!"
      available_ssids=""
      return 0
    fi

    echo "Checking wlan device $wifi_dev (attempt $attempt of $max_attempts)..."
    available_ssids=$( (iw dev "$wifi_dev" scan ap-force | grep -E "SSID:" | sort | uniq) 2>&1) >/dev/null 2>&1
    echo "SSIDs in range:"
    echo "$available_ssids"
    if echo "$available_ssids" | grep "No such device (-19)" >/dev/null 2>&1; then
      handle_missing_device
      echo "Wifi device \"$wifi_dev\" does not exist!"
      # Activate wifi connection so that when the device is reconnected a router will be available
      dhcpcd --rebind "$wifi_dev" >/dev/null 2>&1
      exit 1
    elif echo "$available_ssids" | grep "Network is down (-100)" >/dev/null 2>&1; then
      echo "Network is down!"
      attempt=$((attempt + 1))
      sleep 2
    elif echo "$available_ssids" | grep "Read-only file system (-30)" >/dev/null 2>&1; then
      echo "Running on temporary read-only file system!"
      attempt=$((attempt + 1))
      sleep 2
    elif echo "$available_ssids" | grep "Invalid exchange (-52)" >/dev/null 2>&1; then
      echo "Temporary unavailable (invalid exchange)!"
      attempt=$((attempt + 1))
      sleep 2
    elif echo "$available_ssids" | grep "resource busy (-16)" >/dev/null 2>&1; then
      echo "Wifi device \"$wifi_dev\" is busy!"
      attempt=$((attempt + 1))
      sleep 2
    elif echo "$available_ssids" | grep "SSID: " >/dev/null 2>&1; then
      echo "SSID scan results available, checking list for matching SSID..."
      break
    else
      echo "Wifi device unavailable or no wifi networks found, checking again..."
      attempt=$((attempt + 1))
      sleep 2
    fi
  done

  for ssid in "${ssids[@]}"; do
    if (echo "$available_ssids" | sed 's/^\t*SSID: //g' | grep -e "^${ssid}$") >/dev/null 2>&1; then
      echo "Matching SSID found: $ssid"
      ssid_status="available"
      detected_ssid="$ssid"
      return 0
    fi
  done
}

initialize_system_services
find_ssid

# Connect to a valid wifi network if it's available, otherwise make an isolated wifi network
if [[ "$ssid_status" == "unavailable" ]]; then
  echo "No external wifi network to connect to!"
  if systemctl status hostapd | grep "(running)" >/dev/null 2>&1; then
    echo "Isolated wifi network already started; nothing else to do!"
    exit 0
  elif { wpa_cli status | grep "$wifi_dev"; } >/dev/null 2>&1; then
    echo "Resetting $wifi_dev..."
    wpa_cli terminate >/dev/null 2>&1
    ip addr flush "$wifi_dev"
    ip link set dev "$wifi_dev" down
    rm -r /var/run/wpa_supplicant >/dev/null 2>&1
  fi
  start_isolated_wlan
else
  if systemctl status hostapd | grep "(running)" >/dev/null 2>&1; then
    stop_isolated_wlan
    echo "Connecting to external wifi network..."
    dhcpcd --rebind "$wifi_dev" >/dev/null 2>&1
    fallback_if_unusable_wifi
  elif { wpa_cli -i "$wifi_dev" status | grep 'ip_address'; } >/dev/null 2>&1; then
    echo "Already connected to external wifi network!"
  else
    echo "Connecting to external wifi network..."
    dhcpcd --rebind "$wifi_dev" >/dev/null 2>&1
    fallback_if_unusable_wifi
  fi
fi
