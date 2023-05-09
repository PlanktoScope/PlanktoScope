# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Previously the PlanktoScope could be connected to from 192.168.4.1 (over wifi, when running in wireless AP mode), 192.168.5.1 (over ethernet), and `planktoscope.local` (over wifi or ethernet, from a client device with mDNS support); this meant that Android devices could only connect to the PlanktoScope at 192.168.4.1, as they lack mDNS support. Now, client devices - even those without mDNS support - can connect to the PlanktoScope at `default.planktoscope`, `plankto.scope`, and/or `babaya-koujaini.planktoscope` (where `babaya-koujaini` is replaced with the PlanktoScope's Raspberry Pi's machine ID which is provided by the PlanktoScope's wifi network)
- A [Cockpit](https://cockpit-project.org/) system administration dashboard is now installed and made accessible on port 9090 at URL path /admin/cockpit/ (so e.g. it's accessible at http://plankto.scope:9090/admin/cockpit/)
- [Docker](https://www.docker.com/) is now installed.
- [ufw](https://en.wikipedia.org/wiki/Uncomplicated_Firewall) is now installed, though it is disabled by default.

### Changed

- (Likely user-facing change) The default timezone has been changed to UTC, and we will be using UTC as the standard timezone for all PlanktoScopes.
- (Likely user-facing change) The default wifi country has been changed from `FR` to `US`.
- Previously the autohotspot script would print the MAC addresses and SSIDs of all wifi networks found by scanning. Now it only prints the SSIDs of wifi networks found by scanning and avoids printing duplicate SSIDs, for more concise service logs.
- (Likely user-facing change) Previously the autohotspot script consider receiving an IP address assignment from the connected wifi network as the criterion for determining whether the wifi connection was successful. Now the autohotspot script tries to ping google.com to determine whether the connection was successful, so that the autohotspot script will revert to wireless AP mode if no internet access is available over the wifi network (e.g. if the connected wifi network is actually behaving like a captive portal, which would prevent the PlanktoScope from being accessed via a VPN over the internet - in which case the PlanktoScope would become accessible only over an Ethernet cable). This change is meant to make it easier to fix a PlanktoScope's wifi connection configuration when that configuration makes internet access impossible.
- When the autohotspot script fails to connect to google.com, it will also print some diagnostic information by attempting to ping 1.1.1.1 (the static IP address of Cloudflare DNS, so a ping without DNS lookup) and checking whether the wifi network assigned an IP address to the Raspberry Pi, and reporting the results. This enables beetter troubleshooting of internet access issues on wifi networks.
- Previously the autohotspot script was run every 5 minutes to scan for available wifi networks. Now it is run every 2 minutes, so that the PlanktoScope will connect more quickly to a wifi network which has just appeared.
- Previously the autohotspot script and the dhcpcd service would both try to manage when to start and stop the dnsmasq service. Now, the dnsmasq service always runs. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain.
- Previously the autohotspot script would use a mixture of dhcpcd and wpa_supplicant as entrypoints for wifi network connection management. Now, dhcpcd is used to manage wpa_supplicant, and the autohotspot script only interacts with dhcpcd. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain.
- The `/usr/bin/stepper-disable` and `/usr/bin/autohotspotN` scripts have been moved to `/home/pi/.local/bin/release-gpio-steppers.sh` and `/home/pi/.local/bin/autohotspot.sh`, respectively.
- The `gpio-init.service` systemd service has been renamed to `planktoscope-org.init-gpio-steppers.service`.
- Previously the `en_DK.UTF-8` locale was used for everything. Now it is only used for time, measurements, and paper dimensions, and the `en_US.UTF-8` locale is the base locale for everything else.
- The chrony configuration has been simplified.

### Removed

- nginx is no longer installed, and the file browser on port 80 is removed. This functionality will be replaced with a different file browser before the next release.

### Fixed

- (Major regression fix) Commit [da2d70f](https://github.com/PlanktoScope/PlanktoScope/commit/da2d70f56f741b4abffb557e17f59d8e37183c2f) modified the `flows/main.json` file in a way that broke the file - afterwards Node-RED could no longer load the flows file, giving a "Error adding flows: Cannot read properties of undefined" error because the object Romain added (with fields `license` and `copyright` was an invalid node when Node-RED tried to parse it). Now the proper field values are added so that Node-RED doesn't error out from seeing that object.
- Previously the autohotspot script would not ignore any networks which were commented out in the `/etc/wpa_supplicant/wpa_supplicant.conf` file when checking if any networks found by scanning matched networks specified in the `wpa_supplicant.conf` file; now it ignores them, so that commented-out networks don't prevent the autohotspot from going into wireless AP mode.
- Previously the autohotspot script would always wait 20 seconds after attempting to connect to a wifi network before checking whether the connection was successful, even if it didn't actually need to wait 20 seconds. Now the autohotspot script repeatedly attempts to ping google.com with a timeout of 2 seconds per attempt and a maximum of 10 attempts, so that the autohotspot script only waits as long as a necessary to determine that a wifi network has succeeded.
- Previously the autohotspot script could decide that the SSID scan results were available even if no SSIDs were found (despite local wifi networks bbeing active). Now an empty SSID scan result is treated as a condition where a re-scan is required.
- Previously the log messages from the autohotspot script had inconsistent capitalization and grammar, and slightly unclear wording. Those have now been made more clear and consistent.
- The `adafruit-blinka` and `adafruit-platformdetect` dependencies are now updated to their latest version (though this is not yet version-locked in the `requirements.txt` file).

## v2.3 - 2021-12-20

All changes in v2.3 and before predate recorded history; we may eventually try to fill in this gap
in this changelog.
