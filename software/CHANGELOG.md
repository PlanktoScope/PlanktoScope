# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Calendar Versioning](https://calver.org/) with a `YYYY.MM.patch` scheme.

## Unreleased

### Added

- (System: networking) Previously the PlanktoScope could be connected to from 192.168.4.1 (over wifi, when running in wireless AP mode), 192.168.5.1 (over ethernet), and `planktoscope.local` (over wifi or ethernet, from a client device with mDNS support); this meant that Android devices could only connect to the PlanktoScope at 192.168.4.1, as they lack mDNS support. Now, client devices - even those without mDNS support - can connect to the PlanktoScope at `home.planktoscope`, and/or a URL like `babaya-koujaini.planktoscope` (where `babaya-koujaini` is replaced with the PlanktoScope's Raspberry Pi's machine ID, which is also part of the name of the PlanktoScope's wifi network)
- (System: administration, troubleshooting, GUI) A [Cockpit](https://cockpit-project.org/) system administration dashboard is now installed and made accessible on port 9090 at URL path /admin/cockpit/ (so e.g. it's accessible at http://plankto.scope:9090/admin/cockpit/)
- (System: administration) [Docker](https://www.docker.com/) is now installed. Upon the first boot-up of the SD card, Docker Swarm mode is initialized; for now, only a single-member swarm (consisting of the PlanktoScope's Raspberry Pi itself) is supported.
- (System: networking) [ufw](https://en.wikipedia.org/wiki/Uncomplicated_Firewall) is now installed, though it is disabled by default.

### Changed

- (User-facing change; Application: GUI) Previously, the Node-RED dashboard was accessed on the path `/ui` on port 1880, e.g. with URLs like `http://planktoscope.local:1880/ui` or `http://192.168.4.1:1880/ui`; now, it must be accessed on the path `/ps/node-red-v2/ui` on port 1880, e.g. with URLs like `http://planktoscope.local:1880/ps/node-red-v2/ui` or `http://192.168.4.1:1880/ps/node-red-v2/ui`.
- (User-facing change; System: GUI) Previously, the Node-RED flow editor was accessed directly on port 1880, e.g. with URLs like `http://planktoscope.local:1880` or `http://192.168.4.1:1880`; now, it must be accessed on the path `/admin/ps/node-red-v2` on port 1880, e.g. with URLs like `http://planktoscope.local:1880/admin/ps/node-red-v2` or `http://192.168.4.1:1880/admin/ps/node-red-v2`.
- (Likely user-facing change; System) The default timezone has been changed to UTC, and we will be using UTC as the standard timezone for all PlanktoScopes.
- (Likely user-facing change; System: networking) The default wifi country has been changed from `FR` to `US`.
- (System: networking) Previously the autohotspot script would print the MAC addresses and SSIDs of all wifi networks found by scanning. Now it only prints the SSIDs of wifi networks found by scanning and avoids printing duplicate SSIDs, for more concise service logs.
- (Likely user-facing change; System: networking) Previously the autohotspot script consider receiving an IP address assignment from the connected wifi network as the criterion for determining whether the wifi connection was successful. Now the autohotspot script tries to ping google.com to determine whether the connection was successful, so that the autohotspot script will revert to wireless AP mode if no internet access is available over the wifi network (e.g. if the connected wifi network is actually behaving like a captive portal, which would prevent the PlanktoScope from being accessed via a VPN over the internet - in which case the PlanktoScope would become accessible only over an Ethernet cable). This change is meant to make it easier to fix a PlanktoScope's wifi connection configuration when that configuration makes internet access impossible.
- (System: networking) When the autohotspot script fails to connect to google.com, it will also print some diagnostic information by attempting to ping 1.1.1.1 (the static IP address of Cloudflare DNS, so a ping without DNS lookup) and checking whether the wifi network assigned an IP address to the Raspberry Pi, and reporting the results. This enables better troubleshooting of internet access issues on wifi networks.
- (System: networking) Previously the autohotspot script was run every 5 minutes to scan for available wifi networks. Now it is run every 2 minutes, so that the PlanktoScope will connect more quickly to a wifi network which has just appeared.
- (System: networking) Previously the autohotspot script and the dhcpcd service would both try to manage when to start and stop the dnsmasq service. Now, the dnsmasq service always runs. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain.
- (System: networking) Previously the autohotspot script would use a mixture of dhcpcd and wpa_supplicant as entrypoints for wifi network connection management. Now, dhcpcd is used to manage wpa_supplicant, and the autohotspot script only interacts with dhcpcd. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain.
- (System: networking) The autohotspot script has undergone a major refactoring, which may accidentally introduce bugs.
- (System) The `/usr/bin/stepper-disable` and `/usr/bin/autohotspotN` scripts have been moved to `/home/pi/.local/bin/release-gpio-steppers.sh` and `/home/pi/.local/bin/autohotspot.sh`, respectively.
- (System) The `gpio-init.service` systemd service has been renamed to `planktoscope-org.init-gpio-steppers.service`.
- (System) Previously the `en_DK.UTF-8` locale was used for everything. Now it is only used for time, measurements, and paper dimensions, and the `en_US.UTF-8` locale is the base locale for everything else.
- (System) The chrony configuration has been simplified.
- (System, Dependencies) The base OS is now the 2023-05-03 release of Raspberry Pi OS Bullseye.

### Removed

- (User-facing removal; System: administration) nginx is no longer installed, and the file browser on port 80 is removed. This functionality will be replaced with a different file browser before the next release.
- (User-facing removal; System) The Raspberry Pi's CPU is no longer overclocked.

### Fixed

- (Major fix of a regression after the last release; Frontend) Commit [da2d70f](https://github.com/PlanktoScope/PlanktoScope/commit/da2d70f56f741b4abffb557e17f59d8e37183c2f) modified the `flows/main.json` file in a way that broke the file - afterwards Node-RED could no longer load the flows file, giving a "Error adding flows: Cannot read properties of undefined" error because the object Romain added (with fields `license` and `copyright` was an invalid node when Node-RED tried to parse it). Now the proper field values are added so that Node-RED doesn't error out from seeing that object.
- (Major quality-of-life improvement for users; Dependencies) The `adafruit-blinka` and `adafruit-platformdetect` dependencies are now updated to their latest version (though this is not yet version-locked in the `requirements.txt` file).
- (System: networking) Previously the autohotspot script would not ignore any networks which were commented out in the `/etc/wpa_supplicant/wpa_supplicant.conf` file when checking if any networks found by scanning matched networks specified in the `wpa_supplicant.conf` file; now it ignores them, so that commented-out networks don't prevent the autohotspot from going into wireless AP mode.
- (System: networking) Previously the autohotspot script would always wait 20 seconds after attempting to connect to a wifi network before checking whether the connection was successful, even if it didn't actually need to wait 20 seconds. Now the autohotspot script repeatedly attempts to ping google.com with a timeout of 2 seconds per attempt and a maximum of 10 attempts, so that the autohotspot script only waits as long as a necessary to determine that a wifi network has succeeded.
- (System: networking) Previously the autohotspot script could decide that the SSID scan results were available even if no SSIDs were found (despite local wifi networks bbeing active). Now an empty SSID scan result is treated as a condition where a re-scan is required.
- (System: networking) Previously the log messages from the autohotspot script had inconsistent capitalization and grammar, and slightly unclear wording. Those have now been made more clear and consistent.

## v2.3.0 - 2021-12-20

### Added

- A basic working image segmenter.
- Direct connections over Ethernet.
- A "Lab culture" sample type, where location is set to the South Pole, and sample collection time and date are set by default to the current time and date on the Raspberry Pi but can be changed. ([#74](https://github.com/PlanktoScope/PlanktoScope/issues/74))
- A "Test" sample type, where location is set to the South Pole, and sample collection time and date are always set to the current time and date on the Raspberry Pi.
- A selector in the Node-RED dashboard for the machine hardware version ([#98](https://github.com/PlanktoScope/PlanktoScope/issues/98))

### Changed

- Various parts of the UI (we do not have a list of specific changes).
- Node-RED is now upgraded to v2.0 ([#97](https://github.com/PlanktoScope/PlanktoScope/issues/97))
- The base OS is now the 2021-12-03 release of Raspberry Pi OS Buster.

### Fixed

- Various issues with accessing the Node-RED dashboard via http://planktoscope.local:1880/ui .
- Various issues with Node-RED ([#80](https://github.com/PlanktoScope/PlanktoScope/issues/80), [#91](https://github.com/PlanktoScope/PlanktoScope/issues/91), [#87](https://github.com/PlanktoScope/PlanktoScope/issues/87), [#96](https://github.com/PlanktoScope/PlanktoScope/issues/96))

## v2.2.1 - 2021-05-10

### Added

- The ability for developers to change the PlanktoScope repository to a development branch from the Node-RED dashboard.

### Fixed

- Various bugs (we do not have a list of specific changes)

## v2.2.0 - 2021-02-23

### Added

- Support for Raspberry Pi HQ cameras.
- Control of image white balance.
- A Node-RED dashboard panel to copy all data from `/home/pi/data` to a USB drive.
- Integrity check of the generated files (for now only for raw pictures and `metadata.json` files). A file called `integrity.check` is created alongside the images. This file contains one line per file, with the filename, its size and a checksum of both its filename and its content.
- A file gallery to browse data files in the `/home/pi/data` directory.
- A way to update the PlanktoScope software repository on the Raspberry Pi.
- A Node-RED dashboard panel to choose a wifi network to connect to.
- A Node-RED tab to enter the configuration of the hardware.

### Changed

- (Breaking change) The UI has been changed (we do not have a list of specific changes)

### Fixed

- Random camera crash solved: instead of using the python picamera library, we now use a compiled binary, `raspimjpeg`, controlled through a FIFO pipe

## v2.1.0 - 2020-10-14

### Added

- If the Raspberry Pi is configured (via the `/etc/wpa_supplicant/wpa_supplicant.conf` file) to connect to an existing wifi network, it will try to connect to the network; and it will only start its own wifi hotspot if it failed to connect.
- If the Raspberry Pi is connected to the internet via its Ethernet port, it will share internet access to devices connected to the Raspberry Pi's wifi hotspot.
- (Documentation) Information has been added about ribbon cable assembly.
- (Documentation) Information has been added about how to back up the SD card.

### Changed

- (Breaking change) The OS is now based on Raspberry OS Lite, so there is no graphical desktop.
- (Breaking change) The wifi network is now named `PlanktoScope`, and the password to it is now `copepode`.
- (Breaking change) The default user is now `pi`, and the default password is `copepode` for this user.
- (Breaking change) All raw and processed data files are now stored in the directory `/home/pi/data`.
- The software has undergone a major refactoring, which may accidentally introduce some bugs.
