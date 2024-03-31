# Startup

This reference document is a companion to our explanation about the [PlanktoScope software as an operating system](../architecture/os.md), particularly its discussion of the operating system's [boot sequence](../architecture/os.md#boot-sequence) and its explanation of the various system services provided with the operating system. Specifically, this document lists information about what happens when the PlanktoScope is powered on.

## Services

The PlanktoScope OS's daemons and system services (beyond what is already provided by the default installation of the Raspberry Pi OS) are defined with the following boot sequencing relationships:

### Software deployment & execution

- `dockerd` (described above and managed by `docker.service`) can start before network connectivity has been established; this is not the default behavior for `dockerd`.

- `forklift-apply.service`, which uses the `forklift` tool to start all Docker Compose applications, runs after `docker.service` has started. Docker Compose applications managed with `forklift` are sequenced by `forklift-apply.service` according to the resource dependency relationships declared by the Forklift packages which provide those applications.

- All daemons & background processes not described in the rest of this section are sequenced by systemd according to the systemd unit dependency relationships specified by the default systemd service files installed with the APT packages which provide those programs.

### Networking

- `enable-interface-forwarding.service`, which configures the Linux kernel firewall's IP packet filter rules to forward packets between the Raspberry Pi's network interfaces (to allow the Raspberry Pi to act as a network router), runs before network connectivity is considered to have been established.

- `autohotspot` (described above) runs after `forklift-apply.service` and `enable-interface-forwarding.service` have started (so that the PlanktoScope's web browser-based user interfaces are ready for connections before the PlanktoScope's Wi-Fi hotspot is started) and before network connectivity is considered to have been established.

- `planktoscope-org.update-machine-name.service` updates a file with a PlanktoScope machine name generated from the Raspberry Pi's randomly-generated, persistent serial number.

- `planktoscope-org.update-hostname-machine-name.service` updates the OS's hostname with the PlanktoScope's machine name and runs before `dnsmasq` starts, before `avahi-daemon.service` starts, and before any network interfaces start to be configured.

- `planktoscope-org.update-hosts-machine-name.service` updates `dnsmasq`'s hosts file with the PlanktoScope's machine name and runs before `dnsmasq` starts and before any network interfaces start to be configured.

- `planktoscope-org.update-hostapd-ssid-machine-name.service` updates `hostapd`'s configured Wi-Fi hotspot SSID with the PlanktoScope's machine name and runs before `hostapd` starts.

- `planktoscope-org.avahi-alias-pkscope.local.service` and `planktoscope-org.avahi-alias-planktoscope.local.service` configure the Avahi daemon (provided by the Raspberry Pi OS) to also resolve mDNS names `pkscope.local` and `planktoscope.local`, respectively, to IP addresses which are usable by devices connected to the PlanktoScope by a direct connection between their respective network interfaces.

### User interface

- `planktoscope-org.update-cockpit-origins-machine-name.service` updates Cockpit's configuration file with the PlanktoScope's machine name and runs before any network interfaces start to be configured.

- The PlanktoScope Node-RED dashboard (managed by `nodered.service`) starts after `planktoscope-org.update-machine-name.service` has started, to ensure that the Node-RED dashboard has the correct machine name. (In the future the PlanktoScope Node-RED dashboard will instead be run as a Docker container and will be managed by `forklift`.)

### PlanktoScope-specific hardware abstraction

- The PlanktoScope hardware controller (managed by `planktoscope-org.device-backend.controller-{adafruithat or planktoscopehat}.service`) starts after `forklift-apply.service` (which manages Mosquitto, described above) and `nodered.service` have started, to ensure that the PlanktoScope hardware controller broadcasts the detected camera model name only after the PlanktoScope Node-RED dashboard is ready to receive that broadcast. (In the future the PlanktoScope hardware controller will instead be run as a Docker container and will be managed by `forklift`.)
