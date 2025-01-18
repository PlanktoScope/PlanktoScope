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

- `overlay-etc.service` runs after `overlay-sysroot.service` and  `systemd-machine-id-commit.service` , and before `systemd-sysctl.service` and `overlay-fs.target`.

- `start-overlaid-units.service` runs after `overlay-fs.target` and `basic.target`.

- `bind-.local-share-forklift-stages@home-pi.service` runs after `-.mount`, `home.mount`, and `basic.target`.

- `forklift-apply.service`, which uses the `forklift` tool to start all Docker Compose applications, runs after `docker.service` has started. Docker Compose applications managed with `forklift` are sequenced by `forklift-apply.service` according to the resource dependency relationships declared by the Forklift packages which provide those applications.

### Networking

For descriptions of the various targets (e.g. `sysinit.target`, `network-pre.target`) referred to below, see [systemd's bootup process](https://www.freedesktop.org/software/systemd/man/latest/bootup.html) and [systemd's special targets](https://www.freedesktop.org/software/systemd/man/latest/systemd.special.html):

- `generate-machine-name.service` and `generate-hostname-templated.service` runs before `sysinit.target`.

- `update-hostname.service` runs after `generate-hostname-templated.service` and `systemd-hostnamed.service` but before `network-pre.target`.

- `assemble-dnsmasq-config-templated.service` runs after `generate-machine-name.service` and `generate-hostname-templated.service` but before `dnsmasq.service`.

- `assemble-hosts-templated.service` and `assemble-hosts.service` run after `generate-machine-name.service` and `generate-hostname-templated.service` but before `dnsmasq.service` and `network-pre.target`.

- `enable-interface-forwarding-between.service` runs before `network-online.target`.

- `enable-interface-forwarding-inbound.service` runs before `network-online.target`.

- `assemble-hostapd-config-templated.service` and `assemble-hostapd-config.service` run after `generate-machine-name.service` and `generate-hostname-templated.service` but before `hostapd.service`.

- The `hostapd` daemon is manually started and stopped by `autohotspot.service`.

- `autohotspot.service` runs after `forklift-apply.service` and `enable-interface-forwarding-between.service` and ``enable-interface-forwarding-inbound.service`` have started (so that the PlanktoScope's web browser-based user interfaces are ready for connections before the PlanktoScope's Wi-Fi hotspot is started) and before network connectivity is considered to have been established. It is re-run every one or two minutes by `autohotspot.timer`.

- `planktoscope-mdns-alias@pkscope.service` and `planktoscopemdns-alias@planktoscope.service` configure the Avahi daemon (provided by the Raspberry Pi OS) to also resolve mDNS names `pkscope.local` and `planktoscope.local`, respectively, to an IP address (192.168.4.1) which is usable by devices connected to the PlanktoScope by a direct connection between their respective network interfaces.

### User interface

- `assemble-cockpit-config.service`, `assemble-cockpit-origins.service`, and `assemble-cockpit-origins-templated.service` update Cockpit's configuration file  from drop-in config file fragments in `/etc/cockpit/cockpit.conf.d`, `/etc/cockpit/origins.d`, and `/etc/cockpit/origins-templates.d`, respectively. They run after `generate-machine-name.service` and `generate-hostname-templated.service` and before `cockpit.service`.

- `ensure-ssh-host-keys.service` regenerates the SSH server's host keys if the keys are missing, and runs before `ssh.service`.

- The PlanktoScope Node-RED dashboard (managed by `nodered.service`) starts after `planktoscope-org.update-machine-name.service` has started, to ensure that the Node-RED dashboard has the correct machine name. (In the future the PlanktoScope Node-RED dashboard will instead be run as a Docker container and will be managed by `forklift`.)

### PlanktoScope-specific hardware abstraction

- The PlanktoScope hardware controller (managed by `planktoscope-org.device-backend.controller-{adafruithat or planktoscopehat}.service`) starts after `forklift-apply.service` (which manages Mosquito) and `nodered.service` have started, to ensure that the PlanktoScope hardware controller broadcasts the detected camera model name only after the PlanktoScope Node-RED dashboard is ready to receive that broadcast. (In the future the PlanktoScope hardware controller will instead be run as a Docker container and will be managed by `forklift`.)
