# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Calendar Versioning](https://calver.org/) with a `YYYY.MM.patch` scheme
for all releases after `v2.3.0`.
All dates in this file are given in the [UTC time zone](https://en.wikipedia.org/wiki/Coordinated_Universal_Time).

## Unreleased

### Added

- (System: networking) Previously the PlanktoScope could be connected to from 192.168.4.1 (over wifi, when running in wireless AP mode), 192.168.5.1 (over ethernet), and `planktoscope.local` (over wifi or ethernet, from a client device with mDNS support); this meant that Android devices could only connect to the PlanktoScope at 192.168.4.1, as they lack mDNS support. Now, client devices - even those without mDNS support - can connect to the PlanktoScope at `home.planktoscope`, and/or URLs like `clear-field-33719.planktoscope` and `planktoscope-clear-field-33719.local` (where `clear-field-33719` is replaced with the PlanktoScope's Raspberry Pi's machine name, which is also part of the name of the PlanktoScope's wifi network).
- (System: networking) Traffic is now routed with Network Address Translation between the ethernet and wifi network interfaces. This means that if the PlanktoScope has internet access through an Ethernet connection, it will share that internet access to devices connected to its wifi hotspot; and if the PlanktoScope has internet access through a wifi connection, it will share that internet access to devices connected to its Ethernet port.
- (System: networking) Now both `192.168.4.1` and `192.168.5.1` can be used to access your PlanktoScope when your computer is connected directly to it, regardless of whether you are connecting over an Ethernet cable or the PlanktoScope's wifi hotspot.
- (Application: Documentation) An offline copy of the PlanktoScope project documentation is now provided at URL path /ps/docs/ (so e.g. it's accessible at http://home.planktoscope/ps/docs/)
- (System: administration) [Docker](https://www.docker.com/) is now installed. We are using it to deliver various applications in a way that will eventually enable safe and easy upgrades.
- (System: administration, troubleshooting, GUI) A [Cockpit](https://cockpit-project.org/) system administration dashboard is now installed and made accessible at URL path /admin/cockpit/ (so e.g. it's accessible at http://home.planktoscope/admin/cockpit/).
- (System: administration, troubleshooting, GUI) A [filebrowser](https://github.com/filebrowser/filebrowser) instance, allowing you to manage and edit files anywhere in the Raspberry Pi's SD card, is now installed and made accessible at URL path /admin/fs/ (so e.g. it's accessible at http://home.planktoscope/admin/fs/)
- (System: administration, troubleshooting, GUI) A [Portainer](https://www.portainer.io/) administration dashboard for Docker is now installed and made accessible at URL path /admin/portainer/ (so e.g. it's accessible at http://home.planktoscope/admin/portainer/).
- (System: administration, troubleshooting) [w3m](https://en.wikipedia.org/wiki/W3m) is now installed, enabling terminal-based interaction with some wifi network captive portals to obtain internet access on the PlanktoScope. For captive portals which require Javascript, we recommend instead using [browsh](https://www.brow.sh/) as a Docker container; we don't provide browsh in the default SD card image because it adds ~250 MB of dependencies to the image.
- (System: networking) [ufw](https://en.wikipedia.org/wiki/Uncomplicated_Firewall) is now installed, though it is disabled by default. Note: in the future, ufw will probably be removed in favor of firewall management using [firewalld](https://packages.debian.org/buster/firewalld).
- (System: administration) The Node-RED dashboard's "Administration" page now provides an embedded viewer for the operating system's logs, in a new "Operating System" section.
- (Application: GUI) The Node-RED dashboard's "Hardware Settings" page now includes drop-down menu items to select "PlanktoScope v2.4", "PlanktoScope v2.5", and "PlanktoScope v2.6" as allowed hardware versions.
- (Application: GUI) The Node-RED dashboard now generates a notification whenever it restarts the Python hardware controller or segmenter. This provides visibility for the user when changing the hardware version triggers a restart of the Python hardware controller.

### Changed

- (User-facing change; Application: GUI) Previously, the Node-RED dashboard was accessed on the path `/ui` on port 1880, e.g. with URLs like `http://planktoscope.local:1880/ui` or `http://192.168.4.1:1880/ui`; now, it should be accessed on the path `/ps/node-red-v2/ui` on port 80, e.g. with URLs like `http://planktoscope.local/ps/node-red-v2/ui` or `http://192.168.4.1/ps/node-red-v2/ui`.
- (User-facing change; Application: GUI) Previously, the Node-RED dashboard's "Administration" page merged log entries from every component of the Python backend and the Node-RED dashboard. Now, the Node-RED dashboard instead displays links to separate Cockpit log-viewing pages (which by default are accessed with username `pi` and password `copepode`) for the Node-RED dashboard, the backend's hardware controller, and the backend's segmenter, and links to filebrowser directories for all log files created by the backend's hardware controller and segmenter.
- (User-facing change; Application: GUI) Selecting a hardware version on the "Hardware Settings" page of the Node-RED dashboard now causes a default hardware preset for that version to overwrite the entire `hardware.json` file, and the Node-RED dashboard will reload the settings; this prevents the `hardware.json` file from being changed into an inconsistent mixture of settings for different hardware versions, which was the previous (incorrect) behavior. The description on that page is also now more specific about what happens when a hardware version is selected.
- (User-facing removal; System: administration) The file browser on port 80 for viewing datasets has now been moved to path /ps/data/browse/ (so e.g. it's accessible at http://home.planktoscope/ps/data/browse/ ), and it is now implemented using [filebrowser](https://github.com/filebrowser/filebrowser), so that now you can delete folders, download folders, preview images, etc. As before, you can still access this from the "Gallery" page of the Node-RED dashboard.
- (User-facing change; System: GUI) Previously, the Node-RED flow editor was accessed directly on port 1880, e.g. with URLs like `http://planktoscope.local:1880` or `http://192.168.4.1:1880`; now, it must be accessed on the path `/admin/ps/node-red-v2` on port 80 or port 1880, e.g. with URLs like `http://planktoscope.local/admin/ps/node-red-v2` or `http://192.168.4.1/admin/ps/node-red-v2`.
- (User-facing change; System: networking) Previously, PlanktoScope machine names were generated as gibberish words like "Babaxio-Detuiau", and the machine names were used as the names of the private wifi networks generated by the autohotspot script. However, the machine names created by this naming scheme were often difficult to pronounce, remember, and type for people in various languages, and the naming scheme has a low but non-zero risk of generating profane words in some language. Now, PlanktoScope machine names are generated as a combination of two words and a number up to five digits long; words are selected from pre-built lists in a language which can be set based on localization settings. Currently, word lists are only provided in US English, resulting in names like "metal-slope-23501", "conscious-pocket-1684", and "plant-range-10581"; however, word lists can be added for other languages in the future, and a user interface can be provided for changing localization settings.
- (System: networking) Previously, PlanktoScopes all had `planktoscope` as their hostname. Now, the hostname is of the format `planktoscope-<machine-name>`, e.g. `planktoscope-metal-slope-23501` or `planktoscope-plant-range-10581`.
- (Likely user-facing change; System: networking) The default wifi country has been changed from `FR` to `US`.
- (Likely user-facing change; System: networking) Previously the autohotspot script considered receiving an IP address assignment from the connected wifi network as the criterion for determining whether the wifi connection was successful. Now the autohotspot script tries to ping google.com to determine whether the connection was successful, so that the autohotspot script will revert to wireless AP mode if no internet access is available over the wifi network (e.g. if the connected wifi network is actually behaving like a captive portal, which would prevent the PlanktoScope from being accessed via a VPN over the internet - in which case the PlanktoScope would become accessible only over an Ethernet cable). This change is meant to make it easier to fix a PlanktoScope's wifi connection configuration when that configuration makes internet access impossible.
- (System: networking) Previously the autohotspot script would print the MAC addresses and SSIDs of all wifi networks found by scanning. Now it only prints the SSIDs of wifi networks found by scanning and avoids printing duplicate SSIDs, for more concise service logs.
- (System: networking) When the autohotspot script fails to connect to google.com, it will also print some diagnostic information by attempting to ping 1.1.1.1 (the static IP address of Cloudflare DNS, so a ping without DNS lookup) and checking whether the wifi network assigned an IP address to the Raspberry Pi, and reporting the results. This enables better troubleshooting of internet access issues on wifi networks.
- (System: networking) Previously the autohotspot script was run every 5 minutes to scan for available wifi networks. Now it is run every 2 minutes, so that the PlanktoScope will connect more quickly to a wifi network which has just appeared.
- (System: networking) Previously the autohotspot script and the dhcpcd service would both try to manage when to start and stop the dnsmasq service. Now, the dnsmasq service always runs. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain.
- (System: networking) Previously the autohotspot script would use a mixture of dhcpcd and wpa_supplicant as entrypoints for wifi network connection management. Now, dhcpcd is used to manage wpa_supplicant, and the autohotspot script only interacts with dhcpcd. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain. Note that, in the future, wpa_supplicant and dhcpcd may be replaced with [NetworkManager](https://networkmanager.dev/).
- (System: networking) The autohotspot script has undergone a major refactoring, which may accidentally introduce bugs.
- (Application: Backend, GUI) The Node-RED dashboard no longer supervises the Python backend; instead, it delegates that work to systemd.
- (Application: Backend) Log files from the Python backend are no longer saved to `/home/pi`, but instead to subdirectories for the backend components under `/home/pi/device-backend-logs`. Note: the locations of log files may be changed again in the future, and/or file logging may be changed to use a different systemd-based mechanism in the future.
- (System) The `/usr/bin/stepper-disable` and `/usr/bin/autohotspotN` scripts have been moved to `/home/pi/.local/bin/release-gpio-steppers.sh` and `/home/pi/.local/bin/autohotspot.sh`, respectively.
- (System) The `gpio-init.service` systemd service has been renamed to `planktoscope-org.init-gpio-steppers.service`.
- (System) Previously the `en_DK.UTF-8` locale was used for everything. Now it is only used for time, measurements, and paper dimensions, and the `en_US.UTF-8` locale is the base locale for everything else. In the future we may provide GUI functionality for changing the base locale.
- (System) The chrony configuration has been simplified, but it may be broken.
- (System) The default timezone is now officially set to UTC, and we will be using UTC as the standard system time zone for all PlanktoScopes. Previously, the pre-built SD card images provided by this project used UTC as the timezone, but the "Expert Setup" instructions for manually setting up the PlanktoScope software did not specify a time zone to use.
- (System, Dependencies) The base OS is now the 2023-05-03 release of Raspberry Pi OS Bullseye.
- (Application: Backend, Dependencies) The Python backend and Node-RED dashboard's indirect dependencies are now version-locked to improve the reproducibility of the OS setup script independently of when the script is run.

### Deprecated

- (Application: GUI) In a future release (potentially as early as v2023.12.0), the Node-RED editor and Node-RED dashboard will not be accessible at all over port 1880. In this release, you can still access the Node-RED dashboard at path `/ps/node-red-v2/ui` on port 1880, but the embedded image streams and file gallery will not be properly displayed; and you can access the Node-RED editor at path `/admin/ps/node-red-v2` on port 1880. However, you should instead access the Node-RED editor and Node-RED dashboard via the links on the PlanktoScope's landing page.
- (Application: GUI) In a future release (timeline not yet decided), the version of the Node-RED dashboard for the Adafruit HAT will stop receiving new features even as the version of the Node-RED dashboard for the custom PlanktoScope HAT continues receiving new features. However, we will continue to fix bugs in the Node-RED dashboard for the Adafruit HAT, and we will continue to build SD card images for the Adafruit HAT which will also include new features in other software components.

### Removed

- (User-facing removal; Application: GUI) The Node-RED dashboard no longer allows selection of PlanktoScope v1.0 or PlanktoScope v2.2 (waveshare HAT) as the hardware version. Those hardware versions are no longer supported by the software.
- (User-facing removal; System: networking) Now `planktoscope.local` only works for devices connected directly to the PlanktoScope, either via an Ethernet cable or over wifi when the PlanktoScope is running in wireless AP mode. It no longer works on other networks, such as LANs or mesh VPNs, which the PlanktoScope might be connected to. On such networks, the machine-specific mDNS name (of format `planktoscope-<machine-name>.local`) should be used instead.
- (System: administration) The Git-based software update system (exposed in the Node-RED dashboard's "Adminisration" page) has been removed, since it was reported to behave problematically anyways. In the future, we will use a system based on Docker for safer and easier software updates.

### Fixed

- (Major quality-of-life improvement for users; Backend: dependencies) The `adafruit-blinka` and `adafruit-platformdetect` dependencies are now updated to their latest version.
- (System: networking) Previously the autohotspot script would not ignore any networks which were commented out in the `/etc/wpa_supplicant/wpa_supplicant.conf` file when checking if any networks found by scanning matched networks were specified in the `wpa_supplicant.conf` file; now it ignores them, so that commented-out networks don't incorrectly prevent the autohotspot from going into wireless AP mode.
- (System: networking) Previously the autohotspot script would always wait 20 seconds after attempting to connect to a wifi network before checking whether the connection was successful, even if it didn't actually need to wait 20 seconds. Now the autohotspot script repeatedly attempts to ping google.com with a timeout of 2 seconds per attempt and a maximum of 10 attempts, so that the autohotspot script only waits as long as a necessary to determine that a wifi network connection has succeeded.
- (System: networking) Previously the autohotspot script could decide that the SSID scan results were available even if no SSIDs were found (despite local wifi networks being active). Now an empty SSID scan result is treated as a condition where a re-scan is required.
- (System: networking) Previously the log messages from the autohotspot script had inconsistent capitalization and grammar, and slightly unclear wording. Those have now been made more clear and consistent.
- (Application: GUI) Previously, the Node-RED dashboard would often fail to display the log output from the Python backend. Now, it should always make the logs accessible (either by the links to Cockpit log viewer or by the links to the log file browser).

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
