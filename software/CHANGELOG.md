# Changelog

All notable changes to the PlanktoScope's software will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Calendar Versioning](https://calver.org/) with a `YYYY.minor.patch` scheme
for all releases after `v2.3.0`.
All dates in this file are given in the [UTC time zone](https://en.wikipedia.org/wiki/Coordinated_Universal_Time).

## Unreleased

### Added

- (Release) A `fairscope-latest` SD card image is now provided which is identical to the `planktoscopehat` SD card image, except that its default settings configuration file is for the v2.6 PlanktoScope hardware rather than the v2.5 PlanktoScope hardware.
- (System: administration) The Forklift pallet provided by default as the SD card image is now named (and pinned as) the `factory-reset` staged pallet bundle.

### Changed

- (Breaking change; Application: GUI) The default settings configuration file for the `planktoscopehat` SD card image has been reverted to be for the v2.5 PlanktoScope hardware (reverting a change made for v2024.0.0-alpha.2); in v2024.0.0-alpha.2, it was for the v2.6 hardware, while in previous versions it was still for the v2.5 hardware.
- (Release) SD card images are now released with xz compression (as `.img.xz` files) rather than gzip compression (as `.img.gz` files).

### Removed

- (System) `gcc` has been removed from the SD card image, to help reduce SD card image size.

## v2024.0.0-beta.0 - 2024-06-07

### Changed

- (Application: GUI) The ISO selector in the "Optic Configuration" page has been changed from a button group to a slider (with an increment of 50), to enable somewhat finer adjustment of the ISO setting.
- (Breaking change; System) The official SD card images of PlanktoScope OS are now based on the 64-bit (arm64) version of the 2024-03-12 build of Raspberry Pi OS 11 (bullseye), instead of the 32-bit (armhf) version of the 2023-05-03 build of Raspberry Pi OS 11 (bullseye). This increases the performance of the Python segmenter, potentially by a factor of 2. This is expected to break compatibility with the raspimjpeg-based imaging module. If you need a 32-bit version of PlanktoScope OS, you will need to run the OS setup scripts following the PlanktoScope project's documentation's "Non-standard installation" guide for software setup.
- (System: administration) The `machine-name` binary is no longer provided by the OS setup scripts, but instead is provided by Forklift for upgradeability (by upgrading the pallet applied to the Raspberry Pi) & removeability/replaceability (by switching to a different pallet which provides a different version of - or does not provide - the `machine-name`).

### Deprecated

- (System) 32-bit versions of PlanktoScope OS (which can be set up on a 32-bit version of Raspberry Pi OS using the OS setup scripts) are no longer officially supported by the project, but they will continue to work for v2024.0.0 of PlanktoScope OS.

### Removed

- (Application: GUI) The landing page's links to Portainer have been removed, as part of the deprecation in v2024.0.0-alpha.2 of the inclusion of Portainer by default in the PlanktoScope OS's SD card images.

### Fixed

- (Application: GUI) The landing page's links to offline PDF copies of the protocols.io protocols for PlanktoScope operation are no longer broken.
- (Application: GUI) The maximum allowed value in the ISO selector in the "Optic Configuration" page has been reduced from 800 to 650, but only for the planktoscopehat version of the Node-RED dashboard; maximum allowed value is still 800 in the adafruithat version of the Node-RED dashboard. This change is because v2024.0.0-alpha.2's change to the scaling factor for converting between ISO settings and camera gains in the picamera2 library has meant that ISO values above 650 were converted to image gain values which were silently rejected for the Raspberry Pi HQ Camera used PlanktoScopes with hardware version at or above v2.3; this, this change prevents users from setting ISO values which would be silently rejected by the Python hardware controller.

## v2024.0.0-alpha.2 - 2024-04-25

### Added

- (System: administration) The hostname can now be customized by modifying the hostname template (with string interpolation for the machine name) in `/etc/hostname-template`.
- (System: administration) The Cockpit configuration can now be customized by adding configuration snippets as drop-in files in `/etc/cockpit/cockpit.conf.d`, and adding origins to allow in `/etc/cockpit/origins.d`, and adding templated origins (with string interpolation for the machine name, the hostname, and the custom domain) to allow in `/etc/cockpit/origins-templates.d`.
- (System: administration) The dnsmasq configuration can now be customized by adding templated drop-in configuration files (with string interpolation for the machine name, the hostname, and the custom domain) in `/etc/dnsmasq-templates.d`, and by modifying the custom domain (which defaults to `pkscope`) in `/etc/custom-domain`.
- (System: administration) The hostapd configuration can now be customized by adding configuration snippets as drop-in files in `/etc/hostapd/hostapd.conf.d`, and adding templated drop-in files (with string interpolation for the machine name, the hostname, and the custom domain) in `/etc/hostapd/hostapd.conf-templates.d`.
- (System: administration) The hosts file can now be customized can now be customized by adding snippets as drop-in files at `/etc/hosts.d`, and and adding templated snippets (with string interpolation for the machine name, the hostname, and the custom domain) in `/etc/hosts-templates.d`.
- (System: administration) SSH host keys for the SSH server are now automatically generated (if deleted or otherwise missing) during every boot, not just during the first boot.

### Changed

- (Breaking change; Application: backend) Previously, the segmenter's default behavior was to subtract consecutive masks to try to mitigate image-processing issues with objects which get stuck to the flowcell during imaging. However, when different objects occupied the same space in consecutive frames, the subtraction behavior would subtract one object's mask from the mask of the other object in the following frame, which would produce clearly incorrect masks. This behavior is no longer enabled by default; in order to re-enable it, you should enable the `pipeline-subtract-consecutive-masks` feature flag in the `apps/ps/backend/proc-segmenter` package deployment of the local Forklift pallet and re-apply the pallet.
- (Application: backend, GUI) The image quality of frames in the camera preview stream is increased, and frames also have greater width and height.
- (Breaking change; Application: GUI) The default settings configuration file for the `planktoscopehat` SD card image is now for the v2.6 PlanktoScope hardware; previously, it was still for the v2.5 hardware.
- (Breaking change; System: administration) The minimum supported Forklift version for Forklift pallets has increased from v0.4.0 to v0.7.0, due to new integration between Forklift and the filesystem.
- (System: administration) Forklift has been upgraded to v0.7.0, so that pallets are staged before being applied (and with automatic fallback to the last successfully-applied staged pallet), and so that systemd services, `/etc` config files, and some scripts in `/usr` are now managed by Forklift.
- (System: administration) `/etc` is now a overlay filesystem with all manually-edited files saved at `/var/lib/overlays/overrides/etc`.
- (System: administration) `/usr` is now a overlay filesystem with all manually-edited files saved at `/var/lib/overlays/overrides/usr`.

### Deprecated

- (System: administration, troubleshooting; Application: GUI) Portainer will no longer be installed/provided by default after v2024.0.0. This is because it requires inclusion of a relatively large Docker container image in the PlanktoScope OS's SD card image (which is constrained to be up to 2 GB in size so that it can be attached as an upload to GitHub Releases), and because it has an annoying first-time user experience (i.e. that a password must be set within a few minutes of boot, or else the Portainer container must be restarted), and because Dozzle already provides all the basic functionalities needed by most users, and because Portainer has never actually been used for troubleshooting within the past year of the project, and because Portainer has a nontrivial impact on the sizes of the PlanktoScope OS SD card images (which are limited to 2 GB).
- (System: administration; Application: GUI) The "USB backup" functionality of the Node-RED dashboard will be removed in v2024.1.0 (the next release after v2024.0.0). Instead, you should use the datasets file browser for backing up and deleting dataset files on your PlanktoScope.
- (Application: backend) The raspimjpeg-based imaging module in the Python hardware controller has not yet been deleted so that you can change the Python hardware controller code to switch back from the new picamera2-based imaging module if picamera2 ends up causing big problems for you. However, we are deprecating the raspimjpeg-based imaging module, and we will fully delete it in a future release (perhaps v2024.1.0, or perhaps later).

### Fixed

- (Application: GUI) The white balance input validation, which previously only allowed gains between 1.0 and 8.0, now allows gains in the full range allowed by the camera (i.e. between 0.0 and 32.0).
- (Application: backend, GUI) The incorrect scaling factor for converting between ISO settings (in the Node-RED dashboard) and image gains in the new picamera2-based imager is fixed.
- (System: networking) Some uncommon edge cases for packet forwarding (e.g. accessing a one of the PlanktoScope's static IP addresses on a network interface not associated with that static IP address) should work now.

## v2024.0.0-alpha.1 - 2024-03-26

### Changed

- (Breaking change; System: setup) The word `pscopehat` has been replaced with `planktoscopehat` everywhere. This means that any distro setup scripts/commands you previously used with `pscopehat` should be changed.
- (Breaking change; Application: hardware controller) The hardware controller now uses `picamera2` instead of `raspimjpeg` for camera control. This may require different ISO and white balance gains to be used. It also no longer limits the framerate of the camera preview, so the preview stream should adapt to the bandwidth available on your network connection and the system resources available to your web browser; this may increase resource usage on your web browser.

### Deprecated

- (Application: GUI) The current Node-RED dashboard (both the version for the Adafruit HAT and the version for the PlanktoScope HAT) is transitioning to maintenance mode: no new features will be added, and any bugs will be only be fixed if someone volunteers to fix them. The current Node-RED dashboard will be completely replaced by a fully-rewritten Node-RED dashboard, though there is no timeline for completion of that new dashboard. Currently, our plan for deprecating and eventually removing the current Node-RED dashboard is as follows: maintenance mode (no new features, only some bugfixes), then deprecation (no maintenance; not enabled by default, but still installed), then removal (not installed by default, but anyone is free to install it and see if it still works); deprecation will not occur before the rewritten Node-RED dashboard is stable for general-purpose usage. If you have concerns, please share your feedback on GitHub, in an email, or on the PlanktoScope Slack.

### Fixed

- (Breaking change; Application: backend) The default hardware configuration file for the `planktoscopehat` SD card image is now for the v2.6 PlanktoScope hardware; previously, it was (incorrectly) a mixture of v2.5 and v2.6 optical settings.
- (Application: hardware controller) The camera no longer overexposes captured images compared to the camera preview stream, and it no longer produces camera timeout errors.
- (Application: backend) The segmenter should no longer have file permissions errors when trying to read or write files in directories created by Docker or by the Python hardware controller.

## v2024.0.0-alpha.0 - 2024-02-06

### Added

- (System: networking) Added support to share internet access and browser application access over additional network interfaces: a second Wi-Fi module, an additional Ethernet adapter, and a USB networking interface (made by plugging a phone to the Raspberry Pi in USB tethering mode).
- (Application: GUI) The "System Monitoring" page now shows the current system time on the Raspberry Pi and the current time in the web browser of the client device.
- (Application: GUI) The "System Monitoring" page now detects when the Raspberry Pi's system time is very different from the web browser's time, and shows a message and a buttom to change the Raspberry Pi's system time to match the web browser's time.
- (Application: GUI) The "System Monitoring" page's system metrics panel is now collapsible, and it now includes an expandable "Detailed History" subsection to view additional information.
- (System: administration) Added Dozzle as a viewer for Docker container logs.
- (System: networking) Added `lynx` as an alternative terminal web browser to `w3m` for trying to work through captive portals on the Cockpit terminal.
- (System: administration) Added Prometheus as a metrics collection & storage system.
- (System: administration) Added Grafana as a metrics visualization & alerting system.

### Changed

- (Application: GUI) The "System Monitoring" page now uses a Grafana dashboard to display metrics.
- (Application: GUI) The "Fluidic Acquisition" page now uses a numeric text input instead of a slider for adjusting the "Pumped volume" setting, to make it easier to change the setting to a different exact value.
- (Application: GUI) On the "Sample" page, the input fields of the "Sample Location"/"Net Throw Location"/"Net Retrieval Location"/"Culture Date and Time" panels no longer get cleared when pressing the "Validate" button.
- (System: administration) Docker commands can now be run without `sudo`.
- (System: security) `ufw` has been replaced with `firewalld`. However, `firewalld` has not yet been properly configured.
- (System) The PlanktoScope's machine name is now saved to `/var/lib/planktoscope/machine-name` instead of `/home/pi/.local/etc/machine-name`, and it's now saved without a trailing newline.

### Removed

- (Application: GUI) The "System Monitoring" page no longer displays a gauge for the CPU usage, since that information does not need to be monitored to ensure system stability & usability. Instead, a CPU usage history graph can be found in the new "Detailed History" subsection.
- (System: administration) Removed `cockpit-storaged`, which was not useful enough to justify the number (and size of) unneeded dependencies it pulled in for the PlanktoScope software SD card image.
- (System: setup) Removed some unnecessary `apt-get update` commands for a very minor speed-up in the distro setup process.

### Fixed

- (Application: GUI) The "Filtered volume" field (on the "Sample" page) is now saved as the `sample_total_volume` metadata field for all sample types, not just horizontal Plankton tows (corresponding to the "Plankton net", "High Speed Net", and "Tara decknet" sample types).
- (System) Boot time has been made faster by approximately 1 minute.
- (Application: GUI) On Mozilla Firefox, the embedded file browser in the Node-RED dashboard's "Gallery" page should now consistently load with the correct height, instead of sometimes loading with an absurdly small height.
- (System: networking) The Raspberry Pi now correctly detects a phone connected in USB tethering mode to share internet access regardless of when the phone was connected, instead of only detecting that phone if USB tethering mode was enabled early in startup (specifically, before the `dhcpcd` service had started).
- (System: networking) Functionality for automatically updating the `/etc/hosts` file and the hostname based on the machine name has now been split into two separate system services, `planktoscope-org.update-hosts-machine-name.service` and `planktoscope-org.update-hostname-machine-name.service`.

## v2023.9.0 - 2023-12-30

(this release involves no changes from v2023.9.0-beta.2; it's just a promotion of v2023.9.0-beta.2 to a stable release)

## v2023.9.0-beta.2 - 2023-12-02

### Added

- (Application) A hardware configuration file for PlanktoScope hardware v2.6, which was previously missing, has been added. It is now the default hardware configuration file for `pscopehat` builds of the PlanktoScope distro.

### Changed

- (System: infrastructure) Forklift has been upgraded from v0.3.1 to v0.4.0, which includes breaking changes to the schema of Forklift repositories and pallets.

### Removed

- (Application: documentation) The offline documentation included on the PlanktoScope now omits the hardware setup guides.

### Fixed

- (Application: GUI) The white balance gains are now only validated and sent to the backend _after_ the user changes focus away from the input field, instead of being validated and sent 300 ms after the user pauses while editing the value in the input field. This prevents the input validation from being run while the user is still editing the value.
- (Application) The default brightness of the illumination LED for the pscopehat version of the backend (for the custom PlanktoScope HAT) has been reduced; this a temporary workaround to a bug with raspimjpeg where saved images are overexposed even on the default brightness settings with minimum shutter speed and ISO, despite the brightness of raspimjpeg's camera preview looking reasonable (see https://github.com/PlanktoScope/PlanktoScope/issues/259 for details).
- (Application: GUI) In the "Sample" page, when the minimal & maximal fraction size fields and min & max sampling depth fields are both displayed simultaneously, now the adafruithat version of the Node-RED dashboard shows the fraction size fields on one row and the sampling depth fields on another row, rather than showing them in adjacent columns. This way, the adafruithat version of the Node-RED dashboard now matches the layout in the pscopehat version of the Node-RED dashboard.
- (Application: GUI) The "System Monitoring" page now correctly displays the PlanktoScope hardware version in the "Information" panel's "Instrument Type" field.
- (Application: GUI) The "System Monitoring" and "Fluidic Acquisition" pages now display a software version string which is either a tagged version (e.g. `v2023.9.0-beta.1`) when the version is tagged, or else a pseudoversion (e.g. `v2023.9.0-beta.1-36-gf276e84`) which contains an abbreviated commit SHA and a list of the number of commits since the last tagged version. This version string is now also used for the `acq_software` metadata field.
- (Application: GUI) The `process_commit` metadata field is now set once again. Now it depends on the new installer script provided by the [github.com/PlanktoScope/install.planktoscope.community](https://github.com/PlanktoScope/install.planktoscope.community) repo.
- (Application: GUI) The `process_source` metadata field is no longer hard-coded in the Node-RED dashboard. Now it depends on the new installer script provided by the [github.com/PlanktoScope/install.planktoscope.community](https://github.com/PlanktoScope/install.planktoscope.community) repo.
- (System: infrastructure) The SD card setup scripts now apply the Forklift pallet in order to create the Docker Compose services and resources ahead-of-time (rather than waiting for the first boot to do that work), so that the first boot of the SD card image will be much faster.
- (System: infrastructure) The distro setup scripts now work even if they are run from a repository downloaded to some path other than `/home/pi/PlanktoScope`.
- (Application: GUI) The landing page now links to the new project documentation site for online documentation, instead of the old project documentation site.

## v2023.9.0-beta.1 - 2023-09-14

### Added

- (System: networking) The PlanktoScope can now also be accessed using the domain name `pkscope.local` from any web browser where `planktoscope.local` previously worked. We recommend using http://pkscope.local instead of http://planktoscope.local to access your PlanktoScope, for consistency with other domain name formats (see the "Changes" section for details).
- (System: administration, networking) In operating system's networking configuration files which have lines which are automatically generated based on the PlanktoScope's machine name, those lines now have accompanying code comments which explain the correct files to edit in order to make changes which will persist across device reboots.
- (System: administration, networking) You can now check the machine name at `/home/pi/.local/etc/machine-name`. It's updated when the PlanktoScope boots.
- (System: administration; Application: GUI) The Node-RED dashboard now provides some context on the "Administration" page for how to access the logs linked to from that page, and which links to use for providing logs on GitHub or Slack.
- (System: administration; Application: GUI) The Node-RED dashboard now provides some additional information about the side-effects of selecting a hardware version on the "Hardware Settings" page, specifically that the white balance settings will be overwritten.

### Changed

- (Major user-facing change; System: networking) The top-level domain for domain names of format `home.planktoscope` and `{machine-name}.planktoscope` (e.g. http://metal-slope-23501.planktoscope) has been changed from `planktoscope` to `pkscope`, so that the domain names are now of format `home.pkscope` and `{machine-name}.pkscope`. Similarly, the machine-specific mDNS name has been changed from format `planktoscope-{machine-name}.local` to `pkscope-{machine-name}.local`.
- (User-facing change; System: networking) The SSIDs of wifi hotspots generated by the PlanktoScope has been changed from the format `PlanktoScope {machine-name}` to the format `pkscope-{machine-name}`. This makes it easier to determine the machine-specific mDNS URL: just add `.local`, to get `pkscope-{machine-name}.local` (e.g. `pkscope-metal-slope-23501.local`).
- (User-facing change; Application: backend) The Python backend now uses the new machine naming scheme everywhere.
- (System: networking) The default hostname and SSID (used only in certain unexpected situations when a machine name cannot be determined) have both been shortened from `planktoscope` to `pkscope`.
- (System: networking) The SSID format is now specified in `/home/pi/.local/etc/hostapd/ssid.snippet`, instead of `/home/pi/.local/bin/update-ssid-machine-name.sh`.

### Deprecated

- (System: networking) The `planktoscope.local` mDNS name is no longer recommended. We will continue to support it for the foreseeable future (and definitely for at least one year), but we recommend using `pkscope.local` or the machine-specific mDNS name (of format `pkscope-{machine-name}.local`) instead.
- (Application: backend) The Python backend's logs still print machine names in the old naming scheme, to help instrument operators with the naming scheme transition (so that they can identify how each machine was renamed). The machine names in this old naming scheme will be removed in a future release - probably the next release.

### Removed

- (System: administration, networking) The auto-generated `/home/pi/.local/etc/cockpit/origins` file has been removed, because it does not need to be persisted after being generated. Instead, a temporary file is generated and removed after being used.
- (System: administration, networking) The default `/home/pi/.local/etc/hosts` file has been removed from the setup files. Instead, it is now automatically generated by the setup scripts.

### Fixed

- (System: networking) The PlanktoScope no longer generates any machine names or SSIDs which are so long that they prevent the wifi hotspot network from being brought up.
- (Application: backend) The segmenter no longer crashes and fails to respond immediately after attempting to start segmentation.
- (Application: preset settings, GUI) The default setting for the pscopehat version of the Node-RED dashboard is now the 300 um capillary, since that version of the hardware is meant to be used with 300 um capillaries. Previously, the default was the 200 um ibidi slide.
- (Application: preset settings) All default settings for all hardware versions now include a default pixel size calibration of 0.75 um/pixel. Previously, the default settings for v2.1 and v2.3 were missing this setting, which would cause the segmenter to crash when processing datasets generated on PlanktoScopes using the v2.1 or v2.3 hardware settings.
- (Application: preset settings, GUI) The Node-RED dashboard now correctly lists the selected hardware version in the "Hardware Settings" page's "Hardware Version" dropdown menu upon startup.
- (Application: GUI) The Node-RED dashboard now (hopefully) is able to determine the camera type from the Python backend.

## v2023.9.0-beta.0 - 2023-09-02

### Added

- (System: networking) Traffic is now routed with Network Address Translation between the Ethernet and Wi-Fi network interfaces. This means that if the PlanktoScope has internet access through an Ethernet connection, it will share that internet access to devices connected to its Wi-Fi hotspot; and if the PlanktoScope has internet access through a Wi-Fi connection, it will share that internet access to devices connected to its Ethernet port.
- (System: networking) Now both `192.168.4.1` and `192.168.5.1` can be used to access your PlanktoScope when your computer is connected directly to it, regardless of whether you are connecting over an Ethernet cable or the PlanktoScope's Wi-Fi hotspot.
- (System: networking) Previously the PlanktoScope could be connected to from `192.168.4.1` (over Wi-Fi, when running in wireless AP mode), `192.168.5.1` (over Ethernet), and `planktoscope.local` (over Wi-Fi or Ethernet, from a client device with mDNS support); this meant that Android devices could only connect to the PlanktoScope at `192.168.4.1`, as they lack mDNS support. Now, client devices - even those without mDNS support - can connect to the PlanktoScope at `home.planktoscope`, and/or URLs like `clear-field-33719.planktoscope` and `planktoscope-clear-field-33719.local` (where `clear-field-33719` is replaced with the PlanktoScope's Raspberry Pi's machine name, which is also part of the name of the PlanktoScope's Wi-Fi network - e.g. "PlanktoScope clear-field-33719").
- (Application: Documentation) An offline copy of the PlanktoScope project documentation is now provided at URL path `/ps/docs/` (so e.g. it's accessible at http://home.planktoscope/ps/docs/)
- (Application: GUI) The Node-RED dashboard's "Hardware Settings" page now includes a drop-down menu item to select "PlanktoScope v2.5" as an allowed hardware version.
- (Application: GUI, administration) The Node-RED dashboard now generates a notification whenever it restarts the Python backend. This provides visibility for the user when changing the hardware version triggers a restart of the Python backend.
- (System: administration, troubleshooting, GUI) A [Cockpit](https://cockpit-project.org/) system administration dashboard is now installed and made accessible at URL path `/admin/cockpit/` (so e.g. it's accessible at http://home.planktoscope/admin/cockpit/).
- (System: administration, troubleshooting, GUI) A [filebrowser](https://github.com/filebrowser/filebrowser) instance, allowing you to manage and edit files anywhere in the Raspberry Pi's SD card, is now installed and made accessible at URL path `/admin/fs/` (so e.g. it's accessible at http://home.planktoscope/admin/fs/)
- (System: administration, troubleshooting, GUI) A [Portainer](https://www.portainer.io/) administration dashboard for Docker is now installed and made accessible at URL path `/admin/portainer/` (so e.g. it's accessible at http://home.planktoscope/admin/portainer/). Note that you will need to open Portainer within a few minutes after booting (or rebooting) your PlanktoScope in order to create an admin account for Portainer.
- (System: administration) [Docker](https://www.docker.com/) is now installed. We are using it to deliver various applications in a way that will eventually enable safe and easy upgrades.
- (System: administration, troubleshooting) [w3m](https://en.wikipedia.org/wiki/W3m) is now installed, enabling terminal-based interaction with some Wi-Fi network captive portals to obtain internet access on the PlanktoScope. For captive portals which require Javascript, we recommend instead using [browsh](https://www.brow.sh/) as a Docker container; we don't provide browsh in the default SD card image because it adds ~250 MB of dependencies to the image.

### Changed

- (User-facing change; System: administration) The file browser on port 80 for viewing datasets has now been moved to path `/ps/data/browse/` (so e.g. it's accessible at http://home.planktoscope/ps/data/browse/ ), and it is now implemented using [filebrowser](https://github.com/filebrowser/filebrowser), so that now you can delete folders, download folders, preview images, etc. As before, you can still access this from the "Gallery" page of the Node-RED dashboard.
- (User-facing change; Application: GUI) If you navigate the PlanktoScope in your web browser on port 80 (or without specifying a port) (e.g. with URLs like `http://home.planktoscope` or `http://planktoscope.local`), your browser will show a landing page with a list of links for easy access to the Node-RED dashboard, documentation, other embedded applications, and reference information about your PlanktoScope.
- (User-facing change; Application: GUI) Previously, the Node-RED dashboard was accessed on the path `/ui` on port 1880, e.g. with URLs like `http://planktoscope.local:1880/ui` or `http://192.168.4.1:1880/ui`; now, it should be accessed via a link on the landing page.
- (User-facing change; System: networking) Previously, PlanktoScope machine names were generated as gibberish words like "Babaxio-Detuiau", and the machine names were used as the names of the private Wi-Fi networks generated by the PlanktoScope in wireless AP mode. However, the machine names created by this naming scheme were often difficult to pronounce, remember, and type for people in various languages, and the naming scheme sometimes generated names which sounded like curses or insults in some languages. Now, PlanktoScope machine names are generated as a combination of two words and a number up to five digits long; words are selected from pre-built lists in a language which can be chosen based on localization settings. Currently, word lists are only provided in US English, resulting in names like "metal-slope-23501", "conscious-pocket-1684", and "plant-range-10581"; however, word lists can be added for other languages in the future, and a user interface will eventually be provided for changing localization settings.
- (User-facing change; Application: GUI) Selecting a hardware version on the "Hardware Settings" page of the Node-RED dashboard now causes a default hardware preset for that version to overwrite the entire `hardware.json` file, and the Node-RED dashboard will reload the settings; this prevents the `hardware.json` file from being changed into an inconsistent mixture of settings for different hardware versions, which was the previous (incorrect) behavior. The description on the "Hardware Settings" page is also now more specific about what happens when a hardware version is selected.
- (User-facing change; Application: GUI, troubleshooting) Previously, the Node-RED dashboard's "Administration" page merged log entries from every component of the Python backend and the Node-RED dashboard. Now, the Node-RED dashboard instead displays links to separate Cockpit log-viewing pages (which by default are accessed with username `pi` and password `copepode`) for the Node-RED dashboard, the backend's hardware controller, and the backend's segmenter, and links to filebrowser directories for all log files created by the backend's hardware controller and segmenter.
- (User-facing change; System: GUI) Previously, the Node-RED flow editor was accessed directly on port 1880, e.g. with URLs like `http://planktoscope.local:1880` or `http://192.168.4.1:1880`; now, it should be accessed via a link on the landing page .
- (System: networking) Previously, PlanktoScopes all had `planktoscope` as their hostname. Now, the hostname is of the format `planktoscope-<machine-name>`, e.g. `planktoscope-metal-slope-23501` or `planktoscope-plant-range-10581`.
- (Likely user-facing change; System: networking) The default Wi-Fi country has been changed from `FR` (France) to `US` (USA).
- (Likely user-facing change; System: networking) Previously the autohotspot script considered receiving an IP address assignment from the connected Wi-Fi network as the criterion for determining whether the Wi-Fi connection was successful. Now the autohotspot script tries to ping `google.com` to determine whether the connection was successful, so that the autohotspot script will revert to wireless AP mode if no internet access is available over the Wi-Fi network (e.g. if the connected Wi-Fi network is actually behaving like a captive portal, which would prevent the PlanktoScope from being accessed via a VPN over the internet - in which case the PlanktoScope would become accessible only over an Ethernet cable). This change is meant to make it easier to fix a PlanktoScope's Wi-Fi connection configuration when that configuration makes internet access impossible.
- (System: networking, troubleshooting) Previously the autohotspot script would print the MAC addresses and SSIDs of all Wi-Fi networks found by scanning. Now it only prints the SSIDs of Wi-Fi networks found by scanning and avoids printing duplicate SSIDs, for more concise service logs.
- (System: networking, troubleshooting) When the autohotspot script fails to connect to google.com, it will also print some diagnostic information by attempting to ping `1.1.1.1` (the static IP address of Cloudflare DNS, so a ping without DNS lookup) and checking whether the Wi-Fi network assigned an IP address to the Raspberry Pi, and reporting the results. This enables better troubleshooting of internet access issues on Wi-Fi networks.
- (System: networking) Previously the autohotspot script was run every 5 minutes to scan for available Wi-Fi networks. Now it is run every 2 minutes, so that the PlanktoScope will connect more quickly to a Wi-Fi network which has just appeared.
- (System: networking) Previously the autohotspot script and the dhcpcd service would both try to manage when to start and stop the dnsmasq service. Now, the dnsmasq service always runs. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain.
- (System: networking) Previously the autohotspot script would use a mixture of dhcpcd and wpa_supplicant as entrypoints for Wi-Fi network connection management. Now, dhcpcd is used to manage wpa_supplicant, and the autohotspot script only interacts with dhcpcd. This change was made to simplify the network configuration so that it would be easier to understand, troubleshoot, and maintain. Note that, in the future, wpa_supplicant and dhcpcd may be replaced with [NetworkManager](https://networkmanager.dev/).
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

- (User-facing removal; Application: GUI) The Node-RED dashboard no longer allows selection of "PlanktoScope v1.0" or "PlanktoScope v2.2 (waveshare HAT)" as the hardware version. Those hardware versions are no longer supported by the software.
- (User-facing removal; System: networking) Now `planktoscope.local` only works for devices connected directly to the PlanktoScope, either via an Ethernet cable or over Wi-Fi when the PlanktoScope is running in wireless AP mode. `planktoscope.local` no longer works on other networks, such as LANs or mesh VPNs, which the PlanktoScope might be connected to. On such networks, the machine-specific mDNS name (of format `planktoscope-<machine-name>.local`) should be used instead.
- (System: administration) The Git-based software update system (exposed in the Node-RED dashboard's "Adminisration" page) has been removed, since it was reported to behave problematically anyways. In the future, we will use a system based on Docker for safer and easier software updates.

### Fixed

- (Major fault-tolerance improvement; Application: GUI) When an invalid value is entered for the red or blue white balance gain on the Node-RED dashboard's "Optic Configuration" page, that value is now ignored, a notification is displayed about the invalid value, and the white balance gain is reset to the last valid value (loaded from the `hardware.json` configuration file). This fixes [issue #166](https://github.com/PlanktoScope/PlanktoScope/issues/166) by preventing the Node-RED dashboard from saving an invalid value to the `hardware.json` file, which would crash the Python hardware controller after the next boot (or after the next time the Python hardware controller was restarted).
- (Major quality-of-life improvement; Backend: dependencies) The `adafruit-blinka` and `adafruit-platformdetect` dependencies are now updated to their latest version, so that Python hardware controller will work on PlanktoScopes with recent (i.e. post-2021) versions of the Adafruit HAT.
- (Application: GUI, troubleshooting) Previously, the Node-RED dashboard would often fail to display the log output from the Python backend. Now, it should always make the logs accessible (either by the links to Cockpit log viewer or by the links to the log file browser).
- (System: networking) Previously the autohotspot script would not ignore any networks which were commented out in the `/etc/wpa_supplicant/wpa_supplicant.conf` file when checking if any networks found by scanning matched networks were specified in the `wpa_supplicant.conf` file; now it ignores them, so that commented-out networks don't incorrectly prevent the autohotspot from going into wireless AP mode.
- (System: networking) Previously the autohotspot script would always wait 20 seconds after attempting to connect to a Wi-Fi network before checking whether the connection was successful, even if it didn't actually need to wait 20 seconds. Now the autohotspot script repeatedly attempts to ping google.com with a timeout of 2 seconds per attempt and a maximum of 10 attempts, so that the autohotspot script only waits as long as a necessary to determine that a Wi-Fi network connection has succeeded.
- (System: networking) Previously the autohotspot script could decide that the SSID scan results were available even if no SSIDs were found (despite local Wi-Fi networks being active). Now an empty SSID scan result is treated as a condition where a re-scan is required.
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
