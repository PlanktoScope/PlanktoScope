# Operating System

When you flash an SD card image with the PlanktoScope software as part of PlanktoScope's [software setup process](../../../setup/software/standard-install.md), that SD card image consists of the PlanktoScope OS. This document describes the architecture of the PlanktoScope OS as an [_operating system_](https://en.wikipedia.org/wiki/Operating_system), in order to explain:

- How the PlanktoScope software abstracts over the PlanktoScope hardware.

- How the PlanktoScope manages the execution of software programs intended to run on the PlanktoScope.

This information is intended to help you understand:

- The overall design of the PlanktoScope OS, including what functionalities it provides and what software it includes, and why we made certain design decisions.

- How various [software functionalities and responsibilities](../product-specs.md) in the PlanktoScope are divided among the various programs in the PlanktoScope OS.

- How various programs in the PlanktoScope OS support other programs which provide the PlanktoScope's high-level/end-user functionalities.

- What tools you can use to perform software troubleshooting and [system administration](https://en.wikipedia.org/wiki/System_administrator) tasks with the PlanktoScope.

- What kinds of new software you can develop and deploy to run on a PlanktoScope.

Each SD card image of the PlanktoScope's software consists of an _operating system_ for the PlanktoScope; the definition of the term "operating system" can be tricky to demarcate, but for practical purposes this document follows [Bryan Cantrill's characterization of the operating system](https://www.infoq.com/presentations/os-rust/) as the special program that:

- "Abstracts hardware to allow execution of other programs."
- "Defines the liveness of the machine: without it, no program can run."
- Provides some important components including the operating system kernel, libraries, commands, daemons, and other facilities.

This definition is a reasonable description of the PlanktoScope OS, because it's a program which abstracts the following hardware subsystems in a way that enables you to run other programs on the PlanktoScope which need to control or otherwise interact with the PlanktoScope's hardware:

- A Raspberry Pi computer.

- Various input/output devices such as actuators (e.g. the pump, the sample focus-adjustment actuators, and the illumination LED), sensors (e.g. the camera and the GPS module), and information storage devices (e.g. the real-time clock and the EEPROM).

## Software deployment & execution

In order to abstract the Raspberry Pi computer hardware to enable execution of other programs, the PlanktoScope OS merely uses software provided by other open-source projects:

- The PlanktoScope OS is based on - and includes everything from the "Lite" image of - the [Raspberry Pi OS](https://www.raspberrypi.com/documentation/computers/os.html) (which in turn is based on [Debian Linux](https://www.debian.org/)), which provides abstractions for the Raspberry Pi's computer hardware via its [custom Linux kernel](https://www.raspberrypi.com/documentation/computers/linux_kernel.html) and its included libraries. We use the Raspberry Pi OS because it provides Raspberry Pi-specific hardware support which we need and which is not easy to achieve with other [Linux distros](https://en.wikipedia.org/wiki/Linux_distribution); and because it is the Linux distro with the best combination of familiarity, optimization, and maturity for the Raspberry Pi.

- Lower-level system services - including services which we've added on top of the default Raspberry Pi OS - are launched and supervised by [systemd](https://systemd.io/), which provides a system and service manager. We use systemd because the Raspberry Pi OS provides it and relies on it.

- Most of the PlanktoScope's software is (or eventually will be) executed as [Docker](https://www.docker.com/) containers by the [`dockerd`](https://docs.docker.com/get-started/overview/#the-docker-daemon) daemon (which in turn is run by the `docker.service` systemd service). In the PlanktoScope OS, all Docker containers are declaratively specified, configured, and integrated together as [Docker Compose](https://docs.docker.com/compose/) applications. We use Docker because it enables us to isolate programs from each other so that they interact only in specifically-defined ways; this makes it easier for us to configure, integrate, distribute, and deploy the various programs running on the PlanktoScope. Docker does cause some usability quirks (specifically related to user permissions on files) because it runs in rootful mode, so we might consider switching to Podman at some (far?) point in the future - but that would be a serious decision requiring thorough consideration.

The PlanktoScope OS is a 64-bit operating system.

### Boot sequence

Because the PlanktoScope OS is a systemd-based Linux system running on the Raspberry Pi, the PlanktoScope's initial boot sequence is described by external documentation of:

- The [Raspberry Pi 4/5's boot flow](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-4-and-raspberry-pi-5-boot-flow), which consists of two bootloader stages to load the Raspberry Pi's firmware from the Raspberry Pi's SD card; in turn, the firmware loads the Linux kernel from the Raspberry Pi's SD card.

- [Debian's system initialization](https://www.debian.org/doc/manuals/debian-reference/ch03.en.html), which consists of an [initramfs](https://wiki.debian.org/initramfs) stage after the Linux kernel is loaded, followed by a stage for mounting the full filesystem from the Raspberry Pi's SD card and transferring control to the [systemd init process](https://www.debian.org/doc/manuals/debian-reference/ch03.en.html#_systemd_init) as the root user-space process.

- The [systemd system manager's boot behavior](https://www.freedesktop.org/software/systemd/man/latest/bootup.html), which initializes all necessary filesystems, drivers, and system services.

The systemd system manager starts a variety of services added by the PlanktoScope OS which do not exist in the default installation of the Raspberry Pi OS, such as `docker.service`.

Notably as part of basic boot-up (systemd's `basic.target`), systemd will run a set of PlanktoScope OS-specific services for remounting `/etc` and `/usr` as overlay filesystems to merge the following sets of OS files, which are stored/mounted in different locations of the OS's [filesystem](#filesystem):

- OS files provided by the standard Raspberry Pi OS (and a few PlanktoScope OS-specific files added added by the process of building PlanktoScope OS SD card images). Before boot these files are stored at `/etc` and `/usr`, but during boot they are instead found at `/sysroot/etc` and `/sysroot/usr` .
- OS files (including some overrides of files provided by the standard Raspberry Pi OS) managed by Forklift (introduced in the next section) in `/var/lib/forklift/stages`. Storing these files separately makes it easy for them to be atomically added/removed/replaced as a group for reliable [in-place upgrades/downgrades](../../../operation/software-upgrades.md#perform-an-in-place-upgradedowngrade) of the operating system.
- User-applied customizations and overrides to any of those OS files in `/var/lib/overlays/overrides/etc` and `/var/lib/overlays/overrides/usr`. Storing these overrides separately makes it easy for user-made changes to be identified and reverted individually, e.g. as described in our [networking operations guide](../../../operation/networking.md).

### System upgrades

Traditional Linux distros such as the Raspberry Pi OS are designed to run software directly on the host OS using a shared collection of programs and system libraries provided by the Linux distro, and with programs and libraries installed and upgraded in-place directly on the host OS via the package managers provided by the distro, such as [APT](<https://en.wikipedia.org/wiki/APT_(software)>) and [`pip`](https://pip.pypa.io/en/stable/). This causes the following challenges for system administration on the PlanktoScope:

- These packages are not _atomic_ in how they perform system upgrades of installed libraries and programs, so they can fail during the upgrade process (e.g. due to loss of power) in a way that leaves the system in an unknown and un-reproducible state. Such a state can be hard to revert or recover from, short of wiping and re-flashing the Raspberry Pi's SD card with a new OS installation; this would cause the loss of any OS customizations (e.g. installation of additional software) made by the user.

- If an upgrade of all installed programs and libraries results in a system with problems (e.g. bugs in the new version of an installed program), it is hard to completely revert the system to the previous state. Thus, software upgrades involve a trade-off between extra work (e.g. to backup the SD card image before any upgrade) and extra risk (e.g. of software breakage which is hard to revert due to lack of backups).

- Making certain customizations to the OS, such as adding additional programs/libraries or modifying system configuration files, increases the risk of _configuration drift_ in which the system's actual state increasingly diverges over time from the state expected by the PlanktoScope's software maintainers, and thus becomes harder to understand, troubleshoot, or replace. User customizations to the OS cannot be easily separated from the default configuration of the OS, so it is complicated to copy only those customizations in order to drop them onto a fresh installation of the OS from a newer release - especially if the updated OS includes changes to default configurations which conflict with the user customizations.

- Some Python packages required by PlanktoScope-specific programs (namely the PlanktoScope hardware controller and the PlanktoScope segmenter, which are both described in later sections of this document), such as [picamera2](https://github.com/raspberrypi/picamera2) and [opencv-python-headless](https://github.com/opencv/opencv-python), can only be installed as [pre-built wheels](https://pythonwheels.com/) from PyPI when certain versions of system libraries are installed, or else they must be re-compiled from source (which is prohitively slow on the Raspberry Pi for the affected Python packages). This makes dependencies more complicated to manage in maintenance of the PlanktoScope OS for creating and releasing new SD card images with updated software. The reliance on system libraries also increases the risk that a user-initiated upgrade or removal of some of the system's installed APT packages could cause breakage of some `pip`-managed Python packages which had been installed before the change.

All of the factors listed above increase the perceived risk (and/or the required effort for sufficient mitigation of that risk) of accidentally degrading system integrity by keeping all software on the OS up-to-date, which makes it harder for users to receive bugfixes, security patches, and new features in a timely manner. Indeed, outside of systems like phones and Chromebooks (whose operating systems [automatically update themselves](https://chromium.googlesource.com/aosp/platform/system/update_engine/+/HEAD/README.md)), it is common for users of operating systems to avoid installing security updates or OS upgrades out of a fear of breaking their installed software; this is especially common for users who rely on software to operate other scientific instruments, and for good reasons! But the PlanktoScope project currently does not have enough resources to be able to support users stuck on old versions of the PlanktoScope OS; instead, we want to make it easy and safe for all users to always keep their PlanktoScopes - even with customizations to the OS - automatically updated to the latest version of the PlanktoScope OS. We intend to achieve this by:

- Running all PlanktoScope-specific programs which require system libraries (e.g. the PlanktoScope's Python-based programs) in Docker containers - with the required versions of the required system libraries bundled inside those containers - to isolate them from the host OS's libraries installed via APT. This way, APT packages will always be safe to add, upgrade, and remove on the host OS with negligible risk of interfering with PlanktoScope-specific software.

- Enabling (almost) all software and OS configuration files not provided by the default installation of the Raspberry Pi OS to be upgraded and downgraded in-place - either as container images or as replacements of files on the filesystem - with just a reboot. This way, software upgrades can be (perhaps even automatically, for certain kinds of bugs) reverted in-place in case new bugs are introduced, and SD cards will only need to be re-flashed with new images once every few years (i.e. after a new major version of the Raspberry Pi OS is released).

- Enabling most types of user-initiated OS customizations to be version-controlled (in a Git repository) and applied (as a system upgrade/downgrade) together with most of the default configurations added by the PlanktoScope OS over what is already present from the default installation of the Raspberry Pi OS. This way, user-initiated OS customizations can be easy to re-apply automatically even after an SD card is re-flashed with a fresh SD card image of the PlanktoScope OS.

We have implemented most of the systems necessary for these goals. Much of the PlanktoScope's software is not installed or upgraded directly on the host OS via APT or `pip`; instead, we use a (mostly-complete) tool called [`forklift`](https://github.com/PlanktoScope/forklift) which we're developing specifically to support the goals listed above, and which provides a robust way for us to fully manage deployment, configuration, and upgrading of:

- All software which we run using Docker.
- PlanktoScope-specific systemd services.
- PlanktoScope-specific OS configuration files.

Everything managed by `forklift` is version-controlled in a [Git](https://git-scm.com/) repository with a special file structure (so that the repository is called a _pallet_), enabling easy backup and restoration of `forklift`-managed configurations even if the PlanktoScope's SD card is wiped and re-flashed. Forklift is designed so that a pallet is effectively a version-controlled, configurable, declarative [bill of materials](https://en.wikipedia.org/wiki/Bill_of_materials) for software/configuration modules which are composed together by Forklift into a significant layer of the PlanktoScope OS; many kinds of customizations can be performed through a feature-flagging interface which is uniform regardless of the underlying formats of OS configurations involved in those customizations (e.g. as illustrated in our networking operations guides for [adjusting firewalld zone rules](../../../operation/networking.md#make-the-firewall-more-restrictive) and for [disabling one or both Wi-Fi hotspots](../../../operation/networking.md#disable-the-wi-fi-hotspot) and for [disabling access to one or more browser apps](../../../operation/networking.md#disable-all-access-to-privileged-web-browser-apps)). Performing an OS upgrade/downgrade with Forklift is just a matter of running a `forklift` command to switch to a different version of a pallet and then rebooting, as described [in our OS upgrade operations guide](../../../operation/software-upgrades.md#perform-an-in-place-upgradedowngrade).

!!! info

    Forklift was created mostly because the PlanktoScope OS really needs to be built around the Raspberry Pi OS, and because the Raspberry Pi OS is not yet compatible with [bootc](https://containers.github.io/bootc/) (and not even [OSTree](https://ostreedev.github.io/ostree/introduction/)), and because the Raspberry Pi OS also does not yet have mature support for [systemd-sysext](https://www.freedesktop.org/software/systemd/man/latest/systemd-sysext.html), and those systems also don't meet the PlanktoScope OS's full set of requirements - so we don't yet have a sufficiently simple (and free-and-easy-for-project-maintainers-to-operate) alternative to facilitate system upgrades+downgrades and system customization for the PlanktoScope OS.

    In an ideal world, we would not need to use/maintain Forklift in the PlanktoScope OS for achieving the goals which originally motivated the creation of Forklift...or at least Forklift could outsource so much functionality to externally-maintained systems that Forklift could be reduced to a UI wrapper. Or maybe the PlanktoScope OS's goals will later be reduced to the point that Forklift will no longer be very useful for the PlanktoScope OS.

### System customization & configuration

When you're just experimenting and you can tolerate the challenges mentioned above, it's fine to customize the PlanktoScope OS by installing software packages using `pip` directly on the OS and/or by making extensive changes directly to OS configuration files in `/etc`. However, once you actually care about keeping your customizations around - and especially if/when you want to share your customizations with other people - we recommend migrating those customizations into Forklift packages, which are just files and configuration files stored in a specially-structured Git repository which is also published online (e.g. on GitHub, GitLab, Gitea, etc.). `forklift` provides an easy way to [package, publish](https://github.com/PlanktoScope/forklift/blob/main/docs/design.md#app-packaging-and-distribution), [combine, and apply](https://github.com/PlanktoScope/forklift/blob/main/docs/design.md#app-deployment-configuration) customizations via YAML configuration files in Git repositories; this enables easy sharing, configuration, (re-)composition, and downloading of Docker Compose applications, systemd services, and OS configuration files. Configurations of all deployments of Forklift packages on a computer running the PlanktoScope OS are specified and integrated in a single Git repository, a _Forklift pallet_. At any given time, each PlanktoScope has exactly one Forklift pallet applied; switching between Forklift pallets (whether to try out a different set of customizations or to upgrade/downgrade all programs and OS configurations managed by Forklift) is easy and can be done by running just one command (`forklift pallet switch`, described below in the [Applying published customizations](#applying-published-customizations) subsection).

`forklift` organizes apps and configurations into modules called _packages_, but `forklift` is used very differently compared to traditional Linux system package managers like APT, for which you must run step-by-step commands in order to modify the state of your system (e.g. to install some package or install some other package). When using `forklift`, you instead edit configuration files which declare the desired state of your system (or you can instead run some commands provided by `forklift` for common operations, such as in [this example](../../../operation/networking.md#dont-allow-the-planktoscope-to-be-used-as-a-default-gateway-to-the-internet)), and then you ask `forklift` to prepare to make your system match the desired state on its next boot.

#### (No traditional) dependency management

`forklift` is simpler than traditional package managers in some notable ways (because `forklift` is designed to be much less than a traditional package manager), including in the concept of dependencies between packages. For example, Forklift packages cannot specify dependencies on other Forklift packages; instead, they may declare that they depend on certain resources - and you must declare a deployment of some other package which provides those resources. And although `forklift` checks whether resource dependencies between package deployments are satisfied, it does not attempt to solve unmet dependencies (as that is an NP-complete problem which also happens to be a major source of complexity in traditional package managers). If you've worked with the [Go programming language](https://go.dev/) before, resource dependency relationships among Forklift packages are analogous to the relationships between functions which require arguments with particular [interfaces](https://www.alexedwards.net/blog/interfaces-explained) and the types which implement those interfaces, with Forklift resources being analogous to Go interfaces.

This design is intended to facilitate replacement of particular programs with modified or customized versions of those programs. For example, a Forklift package could be declared as providing the same API on the same network port as some other package, so that one package can be substituted for the other while still being treated by Forklift as being compatible with some other program which relies on the existence of that API. `forklift` also checks these resource declarations to ensure that any two packages which would conflict with each other (e.g. by trying to listen on the same network port) will be prevented from being deployed together.

#### Making & publishing customizations

The workflow with `forklift` for developing/testing new OS customizations, such as new package deployments or non-standard configurations of existing package deployments or substitutions of existing package deployments, is as follows:

- Initialize a custom pallet based on (i.e. layered over) an existing pallet, using the `forklift pallet init` command (e.g. `forklift pallet init --from github.com/PlanktoScope/pallet-standard@stable --as github.com/ethanjli/custom-pallet` to make a starter which will be a customization of the latest stable version of the [github.com/PlanktoScope/pallet-standard](https://github.com/PlanktoScope/pallet-standard) pallet, and which can be published to `github.com/ethanjli/custom-pallet`). (Note: the `forklift pallet init` command is not yet implemented, so currently a new pallet can only be created by manually initializing a new Git repository and creating a few YAML files inside it)

- Optionally, create new Forklift packages with definitions of Docker Compose applications and/or systemd services and/or OS configuration files, and configure the deployment of those packages by creating particular files in the pallet.

- Optionally, add one or more files which override files from the existing pallet, in order to override the configurations specified by those files.

- Optionally, add one or more new files, in order to add entirely new configurations.

- Stage the pallet to be applied on the next boot of the PlanktoScope OS, with the `forklift pallet stage` command; when Forklift applies a pallet, it makes the PlanktoScope OS match the configuration of Forklift package deployments specified by the pallet.

- Use `git` to commit changes and (ideally) push them to GitHub, in order to publish your customizations for other people to try out.

(TODO: create a "tutorial"-style page elsewhere in this docs site, and link to it from here; it could be as simple as creating a new pallet which adds a new helloworld-style Node-RED dashboard)

#### Applying published customizations

To apply published customizations (which you or someone else already developed and pushed to a Git repository served by an online host such as GitHub):

1. Stage the customized pallet to be applied on the next boot of the PlanktoScope OS, using the `forklift pallet switch` command (e.g. `forklift pallet switch github.com/PlanktoScope/pallet-segmenter@edge` to use the latest development/unstable version of the [github.com/PlanktoScope/pallet-segmenter](https://github.com/PlanktoScope/pallet-segmenter) pallet).

2. Reboot the Raspberry Pi computer to apply the staged pallet. If the staged pallet cannot be successfully applied during boot, on subsequent boots `forklift` will instead apply the last staged pallet which was successfully applied. (Note: only a failure to update the Docker containers running on the OS is detected as a failed attempt to apply the staged pallet; if you cause problems with the systemd services or other OS configurations provided by your pallet but the Docker containers are all correctly updated, the pallet will still be considered to have been successfully applied.)

Note: currently all of `forklift`'s functionality is only exposed through a command-line interface, but after the `forklift` tool stabilizes we will consider the possibility of adding a web browser-based graphical interface for use by a general audience.

## PlanktoScope-specific hardware abstraction

PlanktoScope-specific hardware modules are abstracted by PlanktoScope-specific programs which expose high-level network APIs (typically using [MQTT](https://mqtt.org/) and/or [HTTP](https://en.wikipedia.org/wiki/HTTP)); other programs should use these APIs in order to interact with the PlanktoScope-specific hardware modules. To provide these APIs, the PlanktoScope OS adds the following services (beyond what is already provided by the default installation of the Raspberry Pi OS):

- [`gpsd`](https://gpsd.gitlab.io/gpsd/): for providing an abstraction for the PlanktoScope's GPS receiver.

- [`chronyd`](https://chrony-project.org/): for managing synchronization of the Raspberry Pi's system clock with the PlanktoScope's GPS receiver and with any time sources available over the Internet.

- The [PlanktoScope hardware controller](https://github.com/PlanktoScope/device-backend/tree/main/control): for controlling PlanktoScope-specific hardware modules and abstracting them into high-level network APIs for other programs to interact with.

## User interface

Traditional operating systems provide a desktop environment with a graphical user interface for operating the computer. By contrast, the PlanktoScope OS provides a set of web browser-based graphical user interfaces for operating the PlanktoScope. This approach was chosen for the following reasons:

- Most people already have a personal computing device (e.g. a phone or laptop). By relying on the user's personal computing device as the graphical interface for the PlanktoScope's software, the PlanktoScope project can reduce hardware costs by omitting a full display from the PlanktoScope hardware.

- The PlanktoScope's computational resources are limited and may often need to be fully used for [data processing](#data-processing) tasks. By offloading real-time interaction (such as rendering of the graphical display, and handling of mouse and keyboard events) to a separate device, we can ensure a smooth user experience even when the PlanktoScope's Raspberry Pi computer is busy with other work.

- When the PlanktoScope is connected to the internet, its web browser-based graphical interfaces can be accessed remotely over the internet from other web browsers. This can be easier to set up - and have lower bandwidth requirements and higher responsiveness - compared to a remote-desktop system for remotely accessing a Raspberry Pi's graphical desktop. This is especially relevant when the PlanktoScope is deployed in a setting where it only has a relatively low-bandwidth internet connection.

The PlanktoScope OS adds the following network services which provide web browser-based graphical user interfaces to help users operate the PlanktoScope:

- A [Node-RED](https://nodered.org/) server which serves over HTTP the PlanktoScope Node-RED dashboard, a graphical interface for end-users to operate the PlanktoScope for image acquisition and image processing.

- A datasets [file browser](https://filebrowser.org/) for viewing, managing, uploading, and downloading image dataset files on the PlanktoScope. These files are generated and used by the PlanktoScope hardware controller and the PlanktoScope segmenter.

- [device-portal](https://github.com/PlanktoScope/device-portal): a PlanktoScope-specific landing page with links for end-users to quickly access the various web browser-based interfaces mentioned above.

The PlanktoScope OS also provides various tools with web browser-based interfaces to aid with system administration and troubleshooting:

- [Cockpit](https://cockpit-project.org/): for performing system-administration tasks such as monitoring system resources, managing system services, viewing system logs, and executing commands in a terminal.

- A system [file browser](https://filebrowser.org/) for viewing, managing, editing, uploading, and downloading any file on the PlanktoScope.

- A log [file browser](https://filebrowser.org/) for viewing, downloading, and deleting log files files generated by the PlanktoScope hardware controller.

- [Dozzle](https://dozzle.dev/): for viewing and monitoring logs of Docker containers.

- [Grafana](https://grafana.com/): for monitoring and exploring metrics stored in Prometheus. Note that this app will no longer be default included on the PlanktoScope OS starting with a future version of the PlanktoScope OS; instead, it will become an optional app which the user would have to manually enable via a Forklift command.

Finally, the PlanktoScope OS adds some terminal tools (beyond what is already provided by the default installation of the Raspberry Pi OS) for administrative tasks which system administrators, software developers, and advanced users may need to use:

- [`forklift`](https://github.com/PlanktoScope/forklift): for configuring, customizing, and updating the PlanktoScope OS.

- [`vim`](https://www.vim.org/): for editing text files.

- [`byobu`](https://www.byobu.org/): for running processes persistently across ephemeral terminal sessions.

- [`git`](https://git-scm.com/): for interacting with Git repositories.

- [`docker`](https://docs.docker.com/reference/cli/docker/) (including [Docker Compose](https://docs.docker.com/compose/)) and [`lazydocker`](https://github.com/jesseduffield/lazydocker): for inspecting Docker containers.

- [`w3m`](https://tracker.debian.org/pkg/w3m) and [`lynx`](https://lynx.invisible-island.net/): for interacting with web pages (such as Wi-Fi network captive portals) directly from the PlanktoScope.

- Various (relatively) low-level tools provided by [`net-tools`](https://manpages.debian.org/bookworm/net-tools/index.html), [`netcat-openbsd`](https://manpages.debian.org/bookworm/netcat-openbsd/index.html), [`nmap`](https://manpages.debian.org/bookworm/nmap/index.html), [`bind9-dnsutils`](https://manpages.debian.org/bookworm/bind9-dnsutils/index.html), and [`avahi-utils`](https://manpages.debian.org/bookworm/avahi-utils/index.html), for troubleshooting (relatively) low-level networking issues.

## Networking

The PlanktoScope is often operated with limited or sporadic internet access, and also in settings with no internet access at all. The PlanktoScope also needs to be deployable in remote settings where the user needs to control the PlanktoScope without being physically present. In both types of situations, the PlanktoScope's web browser-based interfaces need to remain accessible.

We solve this problem by allowing the PlanktoScope to connect to the internet over a known Wi-Fi network, and/or over Ethernet (or USB tethering to a phone sharing its internet access), so that the PlanktoScope's web browser-based interfaces can be accessed over the internet; and by making the PlanktoScope bring up a Wi-Fi hotspot (more formally, a [wireless access point](https://en.wikipedia.org/wiki/Wireless_access_point)) using the Raspberry Pi's integrated Wi-Fi module (or an optional USB Wi-Fi dongle) in the absence of any known Wi-Fi network, so that the web browser-based interfaces can be accessed over the Wi-Fi hotspot. The PlanktoScope implements these functionalities on the available networking-related hardware by using the sofware systems described in the subsections below.

In addition to systemd services enumerated in the subsections below, the standard PlanktoScope OS also adds the following networking-related systemd services:

- `assemble-hosts-templated`: generates a temporary hosts drop-in snippet (which is used by a symlink at `/etc/hosts.d/50-generated-templated`) from drop-in hosts snippet templates at `/etc/hosts-templates.d`.

- `assemble-hosts` generates a temporary hosts file (which is used by a symlink at `/etc/hosts`) from drop-in snippets at `/etc/hosts-templates.d`.

- `report-mac-addresses`: generates a temporary file at `/run/mac-addresses.yml` which enumerates the system's network interfaces and their respective MAC addresses

### Machine naming

Because multiple PlanktoScopes may be placed next to each other and each PlanktoScope needs to generate its own Wi-Fi hotspot with its own name, each PlanktoScope has a semi-unique machine name which is also used for the name of its Wi-Fi hotspot. This machine name, which has the format `{word}-{word}-{number up to five digits long}`, is generated by a stable mapping from the serial number of the PlanktoScope's Raspberry Pi. These serial numbers are randomly generated from a pool of approximately 4.2 billion serial numbers - so while it is possible for the Raspberry Pis of two PlanktoScopes to have the same serial numbers (and thus the same machine names), such a situation is extremely unlikely (and we provide a guide to [manually override the auto-generated machine name](../../../operation/networking.md#change-the-machine-name) if you are unlucky enough to encounter this situation, or if you prefer to choose your own name for your PlanktoScope).

The standard PlanktoScope OS adds the following systemd services (beyond what is already provided by the default installation of Raspberry Pi OS 12) for dynamically generating/updating the hostname at boot:

- `generate-machine-name`: generates a human-readable machine name at `/run/machine-name` from the Raspberry Pi's serial number (or, if that's missing, from `/etc/machine-d`).

- `generate-hostname-templated`: generates a temporary hostname file (which is used by a symlink at `/etc/hostname`) from `/etc/hostname-template`, which can include the machine name from `/run/machine-name`.

- `update-hostname`: updates `systemd-hostnamed` so that the hostname matches what is specified by `/etc/hostname`.

### NetworkManager connections

The PlanktoScope uses [NetworkManager](https://networkmanager.dev/) to handle the different network connection modes which the PlanktoScope supports on its various network interfaces (internal Ethernet port, internal Wi-Fi module, optional USB Ethernet adapter, optional USB Wi-FI dongle, optional USB connection to a phone in tethering mode).

When the PlanktoScope both has internet access and has devices connected to it (e.g. over a Wi-Fi hotspot or over Ethernet), the PlanktoScope shares its internet access with all connected devices; this behavior enables the user to access web pages even when connected to the PlanktoScope. This is implemented in the PlanktoScope OS with NetworkManager's "shared" IPv4 connection type for the PlanktoScope to act as a network router using [Network Address Translation](https://en.wikipedia.org/wiki/Network_address_translation) when it has internet access. When the PlanktoScope shares its connection to a router with a captive portal, connected devices opening the captive portal's web page will appear to the router as if the PlanktoScope itself was opening that captive portal's web page.

The standard PlanktoScope OS provides the following NetworkManager connection profiles, each bound to a specific network interface:

- For interface `eth0`, the Raspberry Pi's internal Ethernet port: connection profile `eth0-default` sets a network configuration which attempts to connect to an Ethernet router and share its internet connection with all other devices connected to the PlanktoScope; if no such router exists, then profile `eth0-default` becomes inactive, and instead profile `eth0-static` (which configures the PlanktoScope to serve as an Ethernet router) becomes active.

- For interface `eth1`, which only appears if a USB-to-Ethernet adapter is plugged in to the Raspberry Pi: connection profile `eth1-default` sets a network configuration which attempts to connect to an Ethernet router and share its internet connection with all other devices connected to the PlanktoScope; if no such router exists, then profile `eth1-default` becomes inactive, and instead profile `eth1-static` (which configures the PlanktoScope to serve as an Ethernet router) becomes active.

- For interface `usb0`, which only appears if a phone in USB tethering mode is plugged in to the Raspberry Pi, connection profile `usb0-default` sets a network configuration which should connect to the phone and share its internet connection with all other devices connected to the Planktoscope.

- For interface `wlan0`, the Raspberry Pi's internal Wi-Fi module: connection profile `wlan0-hotspot` creates a Wi-Fi hotspot (strictly speaking, a Wi-Fi access point network) from the Wi-Fi module, in effect acting like a Wi-Fi router.

- For interface `wlan1`, which only appears if a USB Wi-Fi dongle is plugged in to the Raspberry Pi: connection profile `wlan0-hotspot` creates a Wi-Fi hotspot (strictly speaking, a Wi-Fi access point network) from the USB Wi-Fi dongle, in effect acting like a Wi-Fi router.

The standard PlanktoScope OS adds the following systemd services (beyond what is already provided by the default installation of Raspberry Pi OS 12) for dynamically updating the NetworkManager connection profiles during boot:

- `assemble-networkmanager-connection@eth0-default.service`, `assemble-networkmanager-connection@eth1-default.service`, and `assemble-networkmanager-connection@usb0-default.service`: generate NetworkManager connection profiles from drop-in connection profile snippets in `/etc/NetworkManager/system-connections.d/eth0-default`, `/etc/NetworkManager/system-connections.d/eth1-default`, `/etc/NetworkManager/system-connections.d/usb0-default`, respectively.

- `assemble-networkmanager-connection@eth0-static.service` and `assemble-networkmanager-connection@eth1-static.service`: generate NetworkManager connection profiles from drop-in connection profile snippets in `/etc/NetworkManager/system-connections.d/eth0-static` and `/etc/NetworkManager/system-connections.d/eth1-static`, respectively.

- `assemble-networkmanager-connection-templated@wlan0-hotspot.service` and `assemble-networkmanager-connection-templated@wlan1-hotspot.service`: generate temporary drop-in NetworkManager connection profile snippets (which are used by symlinks at `/etc/NetworkManager/system-connections.d/wlan0-hotspot/40-generated-templated.nmconnection` and `/etc/NetworkManager/system-connections.d/wlan1-hotspot/40-generated-templated.nmconnection`, respectively) from drop-in connection profile snippet templates in `/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot` and `/etc/NetworkManager/system-connections-templates.d/wlan1-hotspot`, respectively.

- `assemble-networkmanager-connection@wlan0-hotspot.service` and `assemble-networkmanager-connection@wlan1-hotspot.service`: generate NetworkManager connection profiles from drop-in connection profile snippets in `/etc/NetworkManager/system-connections.d/wlan0-hotspot` and `/etc/NetworkManager/system-connections.d/wlan1-hotspot`, respectively.

### DHCP & DNS server

When a device connects directly to the PlanktoScope (e.g. via the PlanktoScope's Wi-Fi hotspot, or via an Ethernet cable), it will rely on the one of the PlanktoScope's NetworkManager `-hotspot` or `-static` connection profiles depending on the network interface being used; these connection profiles are of the `shared` IPv4 connection method so that NetworkManager will:

- configure NAT for internet connection sharing.
- launch an instance of [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html) as a [DHCP](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol) server for the PlanktoScope to assign itself certain static IP addresses (e.g. 192.168.4.1) and as a [DNS](https://en.wikipedia.org/wiki/Domain_Name_System) server for the PlanktoScope to assign itself certain domain names (e.g. `home.pkscope`), so that the user can locate and open the PlanktoScope's web browser-based interfaces via those domain names.

The standard PlanktoScope OS adds the following systemd services (beyond what is already provided by the default installation of Raspberry Pi OS 12) for dynamically updating the NetworkManager's `shared`-network dnsmasq configuration during boot:

- `assemble-dnsmasq-config-templated`: generates a temporary dnsmasq drop-in config file (which is used by a symlink at `/etc/NetworkManager/dnsmasq-shared.d/40-generated-templated-config.conf`) from drop-in config file templates at `/etc/NetworkManager/dnsmasq-shared-templates.d`.

### mDNS

In addition to the `.pkscope` domain names set by dnsmasq as a DNS server (which only work on devices connected directly to the PlanktoScope), the PlanktoScope also uses [Avahi](https://avahi.org/) to announce itself under certain [mDNS](https://en.wikipedia.org/wiki/Multicast_DNS) names (e.g. `planktoscope.local`) for all devices it's connected to; these mDNS names may work on networks where the PlanktoScope does not have a static IP address (e.g. because the PlanktoScope is connected to an existing Wi-Fi network). By default, Avahi is configured so that the PlanktoScope announces itself with the mDNS name `{hostname}.local`. For user convenience (and to provide a possibility of guessing a usable URL for accessing the PlanktoScope in situations where the user doesn't remember or can't type the PlanktoScope's full machine name), the PlanktoScope also announces `planktoscope.local` and `pkscope.local` as CNAME aliases for `{hostname}.local`.

The standard PlanktoScope OS adds the following systemd services (beyond what is already provided by the default installation of Raspberry Pi OS 12) to provide mDNS aliases:

- `avahi-publish-cname@pkscope.local` and `avahi-publish-cname@planktoscope.local` configure the Avahi daemon (provided by the Raspberry Pi OS) to also resolve mDNS names `pkscope.local` and `planktoscope.local`, respectively, as aliases for the PlanktoScope's mDNS-based hostname (which has format `{hostname}.local`).

### Firewall

For security reasons, the PlanktoScope includes a network firewall ([firewalld](https://firewalld.org/)) which is active by default with a default configuration in which incoming traffic is only allowed on explicitly-allowed ports/protocols (i.e. [default deny + enumerate goodness](https://www.ranum.com/security/computer_security/editorials/dumb/)). These ports/protocols are:

- ICMP
- DHCP: UDP port 67
- DHCPv6: UDP port 547
- DHCPv6 Client: UDP port 546
- DNS: TCP/UDP port 53
- mDNS: UDP port 5353
- SSH: TCP port 22
- Direct-access fallback for the Cockpit system administration dashboard: TCP port 9090
- HTTP: TCP port 80
- HTTPS: TCP port 443
- MQTT: TCP port 1883

By default, these ports/protocols are allowed on two firewalld zones:

1. `nm-shared`, a firewall zone for devices connecting to the PlanktoScope as a network router (e.g. connected to the PlanktoScope's Wi-Fi hotspot, or connected directly to the PlanktoScope via Ethernet cable)
2. `public`, a firewall zone for devices accessing the PlanktoScope through a network router to which the PlanktoScope is connected.

For more information about these ports/protocols and zones, and for information about disabling the rules for allowing one or more of the ports/protocols listed above, refer to the networking operations guide for [making the firewall more restrictive](http://localhost:8000/operation/networking/#make-the-firewall-more-restrictive).

The standard PlanktoScope OS adds the following systemd services (beyond what is already provided by the default installation of Raspberry Pi OS 12) for the firewall:

- `firewalld`: the firewalld daemon.

- `assemble-firewalld-zone@nm-shared` and `assemble-firewalld-zone@public`: generate firewalld zone XML files for zones `nm-shared` and `public` from drop-in XML snippets in `/etc/firewalld/zones.d/nm-shared` and `/etc/firewalld/zones.d/public`, respectively.

## App/API integration

The standard PlanktoScope OS adds the following common services for integrating network APIs provided by various programs, and to facilitate communication among programs running on the PlanktoScope OS:

- [Mosquitto](https://mosquitto.org/): a server which acts as an MQTT broker. This is used by the PlanktoScope hardware controller and segmenter (described below) to receive commands and broadcast notifications. This is also used by the PlanktoScope's Node-RED dashboard (described below) to send commands and receive notifications. Apps run in Docker containers can access this server over port 1883 through the `mosquitto` Docker bridge network; apps running outside Docker can access this server from host port 1883.

- [Caddy](https://caddyserver.com/) with the [caddy-docker-proxy plugin](https://github.com/lucaslorentz/caddy-docker-proxy): an HTTP server which acts as a [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy) to route all HTTP requests on port 80 from HTTP clients (e.g. web browsers) to the appropriate HTTP servers (e.g. the Node-RED server, Prometheus, and the PlanktoScope hardware controller's HTTP-MJPEG camera preview stream) running on the PlanktoScope. Apps deployed on the PlanktoScope are integrated with the reverse-proxy server by having the Docker containers for those apps include container labels parsed by the caddy-docker-proxy plugin to configure the reverse-proxy server; for apps not exposed in a port on the host, they can be attached to the `caddy-ingress` Docker bridge network so that the reverse proxy can connectly connect to such apps. Currently, the Caddy [site addresses](https://caddyserver.com/docs/caddyfile/concepts#addresses) for the reverse-proxy are for port 80 as an HTTP catch-all; the equivalent Caddyfile site address would be `:80`. Note that this means that HTTPS is currently not supported by the reverse-proxy server's configurations.

## Filesystem

The PlanktoScope OS's filesystem makes some changes from the default Debian/Raspberry Pi OS filesystem structure to make the OS easier to upgrade cleanly with customizations.

### Overlays

The biggest change is that the PlanktoScope OS splits the filesystem up into layers combined with the Linux kernel's [overlay-filesystem](https://docs.kernel.org/filesystems/overlayfs.html) functionality, so that various sets of files in `/etc` and `/usr` can be atomically upgraded/downgraded/replaced together (using Forklift) while still being directly customizable by the system administrator. Specifically, a number of systemd services in the PlanktoScope OS run during early boot to:

- Make a read-only mount (via the `overlay-sysroot` systemd service) of the initial root filesystem, at `/sysroot` (this layout is loosely inspired by [OSTree's filesystem layout](https://ostreedev.github.io/ostree/adapting-existing/)).

- Make a read-only mount of the next Forklift pallet to be applied (via the `bindro-run-forklift-stages-current.service`) from a subdirectory within `/var/lib/forklift/stages` to `/run/forklift/stages/current`.

- Remount `/usr` (via the `overlay-usr` systemd service) as a writable overlay with a Forklift-managed intermediate layer (in a subdirectory within `/var/lib/forklift/stages` which can also be accessed at `/run/forklift/stages/current/exports/overlays/usr`) and `/sysroot/usr` as a base layer; any changes made by the system administrator to files in `/usr` will be transparently stored by the overlay in `/var/lib/overlays/overrides/usr`. This allows Forklift to provide extra files in `/usr` in an atomic way (for atomic upgrades), while overrides made by the system administrator are stored separately. This restructuring of `/usr` also enables factory resetting of the OS even if more packages have been installed using APT, e.g. as discussed in the software reset/upgrade operation guide's [discussion of `apt`/`apt-get`](../../../operation/software-upgrades.md#avoid-touching-aptapt-get).

- Remount `/etc` (via the `overlay-etc` systemd service) as a writable overlay with a Forklift-managed intermediate layer (in a subdirectory within `/var/lib/forklift/stages` which can also be accessed at `/run/forklift/stages/current/exports/overlays/etc`) and `/sysroot/etc` as a base layer; any changes made by the system administrator to files in `/etc` will be transparently stored by the overlay in `/var/lib/overlays/overrides/etc`. This allows Forklift to provide extra files in `/etc` in an atomic way (for atomic upgrades), while overrides made by the system administrator are stored separately. This restructuring of `/etc` also enables factory resetting of the OS even if the user has manually edited any files in `/etc`, e.g. as discussed in the software reset/upgrade operation guide for [resetting the OS](../../../operation/software-upgrades.md#reset-the-planktoscope-os).

- Make a writable mount of `/var/lib/forklift/stages` to `/home/pi/.local/share/forklift/stages` (via the `bind-.local-share-forklift-stages@home-pi` systemd service) so that, when the `pi` user runs `forklift` commands like `forklift pallet switch`, those commands will update `/var/lib/forklift/stages` - and without requiring the use of `sudo`.

- Update systemd (via the `start-overlaid-units` systemd service) with any new systemd units provided via Forklift, so that they will run during boot.

Beyond what is required by the Linux [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs-3.0.html), the PlanktoScope OS sets the following conventions related to filesystem paths:

- Scripts which are provided by Forklift and only used as part of systemd services should be provided in `/usr/libexec`, and Forklift packages should export those scripts to `overlays/usr/libexec` (so, for example, they will be accessible in `/run/forklift/stages/current/exports/overlays/usr/libexec`).

- Systemd units provided by Forklift should be provided in `/usr/lib/systemd/system`, and Forklift packages should export those units to `overlays/usr/lib/systemd/system`. Symlinks to enable those units should be provided in `/etc/systemd/system`, and Forklift packages should export those symlinks to directories within `overlays/etc/systemd/system`.

- Forklift-provided systemd services which dynamically generate temporary files meant to be used in `/etc` should generate those temporary files at stable paths in `/run/overlays/generated/etc`. Forklift packages which provide such systemd services should also provide relative symlinks into those temporary files in `/run/overlays/generated/etc` to be exported into `overlays/etc` as overlays for the corresponding paths in `/etc`. For example, if a package provides a service to dynamically generate a hosts file meant to be used as `/etc/hosts`, that service should generate the file in `/run/overlays/generated/etc/hosts` and the package should export a symlink at `overlays/etc/hosts` which points to `../../run/overlays/generated/etc/hosts`, so that `/etc/hosts` will be a symlink pointing to `/run/overlays/generated/etc/hosts`.

### Config file assembly from drop-in fragments

In Debian Linux (and thus also the standard Raspberry Pi OS), various system services are configured using monolithic configuration files (i.e. all settings are stored in a single file) instead of [drop-in configuration directories](https://unix.stackexchange.com/a/589303) (i.e. settings can be split across multiple files within a directory). The PlanktoScope OS generates some of those monolothic configuration files from drop-in configuration directories, in order to make it easy for users to toggle and/or override individual settings (or individual groups of settings) while continuing to follow any changes for other settings made in future software updates delivered via Forklift. PlanktoScope OS introduces drop-in configuration for the following types of configurations:

- Cockpit: the `/etc/cockpit/cockpit.conf` file is generated from drop-in snippets in `/etc/cockpit/cockpit.conf.d`, and its `WebService` section's `Origins` setting is also generated from drop-in snippets in `/etc/cockpit/origins.d`.

- firewalld: firewall zones in `/etc/firewalld` can be generated from drop-in snippets; for a zone generated at `/etc/firewalld/zones/{zone-name}.xml`, the drop-in snippets are loaded from the `/etc/firewalld/zones.d/{zone-name}` directory.

- The `/etc/hosts` file is generated from drop-in snippets in `/etc/hosts.d`.

- NetworkManager: NetworkManager connection files can be generated from drop-in snippets; for a connection file generated at `/etc/NetworkManager/system-connections/{connection-name}.nmconnection`, the drop-in snippets are loaded from the `/etc/NetworkManager/system-connections.d/{connection-name}` directory.

PlanktoScope OS's general pattern for introducing drop-in configuration is as follows:

- The configuration file `/etc/some/path/here` is replaced (via filesystem overlay over `/etc`) with a symlink to `/run/overlays/generated/etc/some/path/here`. This symlink is delivered via Forklift.

- A systemd service (whose name starts with `assemble-`) runs a script which loads all drop-in files from `/etc/some/path/here.d` in lexicographic order, concatenates them, and writes the output to `/run/overlays/generated/etc/some/path/here`. This systemd service is delivered via Forklift

- Drop-in files in `/etc/some/path/here.d` are delivered (and thus also updated) via Forklift. The delivery of each drop-in file (or logical groups of drop-in files) can be toggled via Forklift package feature flags.

- The user can manually add a new drop-in file in `/etc/some/path/here.d`, and it will be preserved even if other drop-in files are changed via Forklift (whether via OS upgrades/downgrades or via feature flag toggles).

- The user can manually override a Forklift-delivered drop-in file (e.g. by deleting that file or by editing it), and those overrides will continue to override any changes to that file which would otherwise take effect via Forklift (e.g. via OS upgrades/downgrades or via feature flag toggles). The override can be removed by deleting the corresponding file within `/var/lib/overlays/overrides/etc/some/path/here.d`.

For certain system services, certain variables (e.g. the machine name or the hostname) can also be interpolated (by a corresponding systemd service whose name starts with `assemble-` or `generate-` and ends with `-templated`) into drop-in configuration files using a simple templating system: the string `{machine-name}` will be replaced with the machine's auto-generated machine name as specified in `/run/machine-name`, the string `{hostname}` will be replaced with the machine's machine name as specified in `/etc/hostname`, etc. Templating is provided for the following types of configurations:

- The `/etc/hostname` file is replaced (by overlay with Forklift) with a symlink pointing to `/run/overlays/generated/etc/hostname`, which is generated by template-interpolating the template loaded from `/etc/hostname-template`.

- Cockpit: a drop-in snippet at `/etc/cockpit/origins.d/60-generated-templated-names` (which is actually a symlink pointing to a corresponding path within `/run/overlays/generated/etc/...`) is generated by concatenating and template-interpolating the snippets templates loaded from `/etc/cockpit/origins-templates.d/`.

- `/etc/hosts`: a drop-in snippet at `/etc/hosts.d/50-generated-templated` (which is actually a symlink pointing to a corresponding path within `/run/overlays/generated/etc/...`) is generated by concatenating and template-interpolating the snippets templates loaded from `/etc/hosts-templates.d`.

- NetworkManager: drop-in snippets at `/etc/NetworkManager/system-connections.d/wlan0-hotspot/40-generated-templated.nmconnection` and `/etc/NetworkManager/system-connections.d/wlan1-hotspot/40-generated-templated.nmconnection` are generated by concatenating and template-interpolating the snippets templates loaded from `/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot` and `/etc/NetworkManager/system-connections-templates.d/wlan1-hotspot`, respectively. Notably, this is used to set the SSID of the Wi-Fi hotspot according to the PlanktoScope's hostname (which by default is the PlanktoScope's semi-unique machine name).

- dnsmasq (specifically the dnsmasq instance launched by NetworkManager for shared connections): a dnsmasq drop-in configuration file at `/etc/NetworkManager/dnsmasq-shared.d/40-generated-templated-config.conf` (which is actually a symlink pointing to a corresponding path within `/run/overlays/generated/etc/...`) can be generated from templates in `/etc/NetworkManager/dnsmasq-shared-templates.d`.

## Observability & telemetry

Although it is not a high priority yet, we would like to enable operators of large (>10) collections of PlanktoScopes to easily log and monitor the health and utilization of each PlanktoScope and to investigate issues with their PlanktoScopes, regardless of whether each PlanktoScope is deployed locally or remotely. The PlanktoScope OS currently includes the following common services to support system observability and telemetry both for the PlanktoScope OS as a system and for programs running on the PlanktoScope OS:

- [Prometheus](https://prometheus.io/): a server for collecting and storing metrics and for exposing metrics over an HTTP API. Apps deployed on the PlanktoScope can be integrated with the Prometheus server by having the Docker containers for those apps include container labels parsed by Prometheus's [Docker container service discovery mechanism](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#docker_sd_config); for apps not exposed in a port (or via the Caddy reverse-proxy server) on the host, they can be attached to the `prometheus-metrics` Docker bridge network so that the Prometheus server can connectly connect to such apps.

- [Prometheus node exporter](https://github.com/prometheus/node_exporter): for measuring computer hardware and OS monitoring metrics and exposing them over a Prometheus-compatible HTTP API.

In the future, we will instrument other PlanktoScope-specific programs (especially the PlanktoScope hardware controller) to export various metrics for Prometheus to collect and expose.

## Data processing

Because the PlanktoScope collects raw image datasets which are often too large to transfer efficiently over low-bandwidth or intermittent internet connections, the PlanktoScope needs to be able to process raw image data into lower-bandwidth data (e.g. cropped and segmented images of particles in the raw images, or even just counts of different classes of particles) without internet access. In other words, the PlanktoScope must support on-board data processing at the edge. The PlanktoScope OS adds the following services for on-board processing of data generated by the PlanktoScope:

- The [PlanktoScope segmenter](https://github.com/PlanktoScope/device-backend/tree/main/processing/segmenter): for processing raw image datasets acquired by the PlanktoScope hardware controller to detect and extract particles from raw images.

Note: in the future, the PlanktoScope OS will add more on-board services for processing the outputs of the PlanktoScope segmenter, and the PlanktoScope OS may also provide hardware abstractions (such as for [AI accelerator modules](https://en.wikipedia.org/wiki/AI_accelerator)) to support the deployment of neural-network models for data processing.

## Security

Currently, the PlanktoScope OS lacks basic security measures to make it safe for them to be connected to the internet; currently it is the responsibility of system administrators to add extremely basic risk mitigations, for example by following the relevant instructions in the [Networking operation guide](../../../operation/networking.md#secure-your-planktoscope):

- Changing the password of the `pi` user away from the default of `copepode`.

- Password-protecting the Node-RED dashboard editor, which can be used to execute arbitrary commands with root permissions.

- Setting firewall rules.

- Changing the password of the Wi-Fi hotspot away from the default of `copepode`, or disabling Wi-Fi hotspot functionality.

Other risk mitigations will require deeper changes to the PlanktoScope OS, such as:

- Limiting the permissions and capabilities made available to various system services which currently run with root permissions

- Password-protecting web browser-based user interfaces

- Password-protecting network [APIs](https://en.wikipedia.org/wiki/API).

We would like to implement these additional risk mitigations, but security is not yet a high-enough priority for us to work on it with the limited resources available to us 🙃 - if you're interested in computer/network security and you'd like to help us as a volunteer on this project, please contact us!
