# Startup

This reference document is a companion to our explanation about the [PlanktoScope software as an operating system](../architecture/os.md), particularly its discussion of the operating system's [boot sequence](../architecture/os.md#boot-sequence) and its explanation of the various system services provided with the operating system. Specifically, this document lists information about what happens when the PlanktoScope is powered on.

## Services

The PlanktoScope OS's daemons and system services (beyond what is already provided by the default installation of the Raspberry Pi OS) are defined with the following boot sequencing relationships:

### Software deployment & execution

In general:

- `dockerd` (managed by `docker.service`) can start before network connectivity has been established; this is not the default behavior for `dockerd`.

- All daemons & background processes not described in the rest of this page are sequenced by systemd according to the systemd unit dependency relationships specified by the default systemd service files installed with the APT packages which provide those programs.

The PlanktoScope OS's setup scripts provide some system services which are not managed by Forklift, because they are used to integrate Forklift into the OS in order to bootstrap the system services and config files provided by Forklift:

- `overlay-sysroot.service` runs after `-.mount` and `systemd-remount-fs.service`.

- `bindro-run-forklift-stages-current.service` runs after `-mount` and `systemd-remount-fs.service` and before `overlay-fs.target`.

- `overlay-usr.service` runs after `overlay-sysroot.service` and before `overlay-fs.target`.

- `overlay-etc.service` runs after `overlay-sysroot.service` and `systemd-machine-id-commit.service` , and before `systemd-sysctl.service` and `overlay-fs.target`.

- `start-overlaid-units.service` runs after `overlay-fs.target` and `basic.target`.

- `bind-.local-share-forklift-stages@home-pi.service` runs after `-.mount`, `home.mount`, and `basic.target`.

- `forklift-apply.service`, which uses the `forklift` tool to start all Docker Compose applications, runs after `docker.service` has started. Docker Compose applications managed with `forklift` are sequenced by `forklift-apply.service` according to the resource dependency relationships declared by the Forklift packages which provide those applications.

### Networking

For descriptions of the various targets (e.g. `sysinit.target`, `network-pre.target`) referred to below, see [systemd's bootup process](https://www.freedesktop.org/software/systemd/man/latest/bootup.html) and [systemd's special targets](https://www.freedesktop.org/software/systemd/man/latest/systemd.special.html):

- `generate-machine-name.service` and `generate-hostname-templated.service` runs after `local-fs.target` but before `sysinit.target` and `systemd-hostnamed.service`.

- `update-hostname.service` runs after `generate-hostname-templated.service` and `systemd-hostnamed.service` but before `network-pre.target` and `avahi-daemon.service`.

- `assemble-firewalld-zone@nm-shared.service` and `assemble-firewalld-zone@public.service` run before `firewalld.service` and `NetworkManager.service`.

- `assemble-hosts-templated.service` and `assemble-hosts.service` run after `generate-machine-name.service` and `generate-hostname-templated.service` but before `NetworkManager.service` and `network-pre.target`.

- `assemble-dnsmasq-config-templated.service` runs after `generate-machine-name.service` and `generate-hostname-templated.service` but before `NetworkManager.service`.

- `assemble-networkmanager-connection-templated@wlan0-hotspot.service`, `assemble-networkmanager-connection-templated@wlan1-hotspot.service`, `assemble-networkmanager-connection@wlan0-hotspot.service` and `assemble-networkmanager-connection@wlan1-hotspot.service` run after `generate-machine-name.service` and `generate-hostname-templated.service` but before `NetworkManager.service`.

- `assemble-networkmanager-connection@eth0-default.service`, `assemble-networkmanager-connection@eth0-static.service`, `assemble-networkmanager-connection@eth1-default.service`, `assemble-networkmanager-connection@eth1-static.service`, and `assemble-networkmanager-connection@usb0-default.service` run before `NetworkManager.service`.

- `avahi-publish-cname@pkscope.local.service` and `avahi-publish-cname@planktoscope.local.service` run after `update-hostname.service` and `avahi-daemon.service`.

- `report-mac-addresses.service` runs after `network-online.target`. It is re-run every two minutes by `report-mac-addresses.timer`.

### User interface

- `assemble-cockpit-config.service`, `assemble-cockpit-origins.service`, and `assemble-cockpit-origins-templated.service` update Cockpit's configuration file from drop-in config file fragments in `/etc/cockpit/cockpit.conf.d`, `/etc/cockpit/origins.d`, and `/etc/cockpit/origins-templates.d`, respectively. They run after `generate-machine-name.service` and `generate-hostname-templated.service` and before `cockpit.service`.

- `ensure-ssh-host-keys.service` regenerates the SSH server's host keys if the keys are missing, and runs before `ssh.service`.

- The PlanktoScope Node-RED dashboard (managed by `nodered.service`) starts after `generate-machine-name.service` has started, to ensure that the Node-RED dashboard has the correct machine name. (In the future the PlanktoScope Node-RED dashboard will instead be run as a Docker container and will be managed by `forklift`.)

### PlanktoScope-specific hardware abstraction

- The PlanktoScope hardware controller (managed by `planktoscope-org.device-backend.controller.service`) starts after `forklift-apply.service` (which manages Mosquitto) and `nodered.service` have started, to ensure that the PlanktoScope hardware controller broadcasts the detected camera model name only after the PlanktoScope Node-RED dashboard is ready to receive that broadcast. (In the future the PlanktoScope hardware controller will instead be run as a Docker container and will be managed by `forklift`.)
