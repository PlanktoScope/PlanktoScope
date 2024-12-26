# Software Reset & Upgrades

Your PlanktoScope's embedded Raspberry Pi computer has a PlanktoScope-specific operating system (the *[PlanktoScope OS](../reference/software/architecture/os.md)*) with software for operating your PlanktoScope. If you purchased a PlanktoScope, then the SD card you received with your PlanktoScope already includes a particular release of the PlanktoScope OS; if you assembled your own PlanktoScope, then you installed some release of the PlanktoScope OS following the [standard software installation guide](../setup/software/standard-install.md) (or maybe the [non-standard software installation guide](../setup/software/nonstandard-install.md)). This guide provides information to help you either reset the software installed on your PlanktoScope or change to a different (newer or older) release of the PlanktoScope OS.

The PlanktoScope project aims to keep improving the PlanktoScope software by fixing problems and making the software simpler and easier to use, releasing a new version of the software at least once each year. At the same time, we aim to keep the software compatible with all previous officially-released versions of the PlanktoScope hardware. For this reason, we strongly recommend everyone to keep their PlanktoScopes updated to run the latest stable release of the PlanktoScope software; and the PlanktoScope documentation will only support the latest stable release. You can always find the latest stable release at <https://github.com/PlanktoScope/PlanktoScope/releases/latest>, which will redirect you to a web page for a specific release.

All URLs in this guide are written assuming you access your PlanktoScope using [planktoscope.local](http://planktoscope.local) as the domain name; if you need to use a [different domain name](./index.md#access-your-planktoscopes-software) such as [home.pkscope](http://home.pkscope), you should substitute that domain name into the links on this page.

## Back up your data & settings

Before you reset/upgrade/downgrade the software installed on your PlanktoScope, you may want to back up any important data and settings on your PlanktoScope. We recommend everyone to take the following actions:

- You should use the dataset file browser (accessible via a link on our PlanktoScope's landing page, or via [the Node-RED dashboard's Gallery page](./user-interface.md#gallery)) to download any data you don't want to lose.
- You should write down the white balance gains you have calibrated on [the Node-RED dashboard's Optic Configuration page](./user-interface.md#optic-configuration), as those values may be lost depending on how you reset or upgrade/downgrade the PlanktoScope OS.
- You should write down the hardware settings and calibrations you see on [the Node-RED dashboard's Hardware Settings page](./user-interface.md#hardware-settings), as those values may be lost depending on how you reset or upgrade/downgrade the PlanktoScope OS.

Advanced users may also want to take the following actions, depending on what changes they have made:

- If you don't want to write down your white balance gains and hardware settings/calibrations, you can instead back up your PlanktoScope's hardware settings file, which is saved at `/home/pi/PlanktoScope/hardware.json`, for example in the file browser at <http://planktoscope.local/admin/fs/files/home/pi/PlanktoScope/> . This file includes some hidden settings not exposed in the PlanktoScope's Node-RED dashboard - so if you have changed any such settings by editing this file, then you may want to back up this file.
- If you have [changed your PlanktoScope's networking configurations](./networking.md) by editing files in `/etc` (which overrides the default configuration files exported by Forklift into the operating system, as well as configuration files originally provided by the Raspberry Pi OS as part of the PlanktoScope OS), you may want to back up your changes. You can download your changes from within `/var/lib/overlays/overrides/etc`, for example in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/> .
- If you have made extensive changes to your operating system by running `forklift` commands which modified your local Forklift pallet, you may want to back them up by using Git to commit those changes and then push your local Forklift pallet (which is a local Git repository at `/home/pi/.local/share/forklift/pallet`) to a repository (e.g. on GitHub).

## Reset the PlanktoScope OS

Multiple levels of reset are possible; from least-disruptive (and shallowest) to most-disruptive (and most thorough), they are:

1. (Only recommended for advanced users) If you just need to reset some or all of your operating system configuration file changes (such as those described in the [networking operations guide](./networking.md)) back to the default settings for the PlanktoScope OS, then you can just delete the relevant files (or you can even delete all files) within `/var/lib/overlays/overrides/etc/` (for example in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/> ) and then reboot your PlanktoScope immediately afterwards.

2. (Only recommended for advanced users) If you want to reset the running software back to the original release of the PlanktoScope OS provided with your SD card image, while keeping any customizations you have made to override default PlanktoScope OS configurations (such as those described in the [networking operations guide](./networking.md)), then you can run the following command on your PlanktoScope (for example in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> ) and then reboot your PlanktoScope:

    ```sh
    forklift stage set-next --no-cache-img factory-reset
    ```

    This reset will only have an effect if you had previously run a `forklift` command for configuring the OS; otherwise, it will not cause any visible change to your PlanktoScope. If your PlanktoScope is [connected to the internet](./networking.md#connect-your-planktoscope-to-the-internet), you can also omit the `--no-cache-img` flag, in order to ensure that the PlanktoScope will have all necessary programs at the originally-required versions before you reboot (if you never previously took manual action to delete any Docker container images from your PlanktoScope, you don't need to worry about this and you can keep the `--no-cache-img` flag in the command).

3. (Recommended for everyone) If you want to completely wipe your SD card and reset everything, then you should re-flash your PlanktoScope's SD card. You can do this by writing an SD card image to the SD card, following the instructions in our [standard software installation guide](../setup/software/standard-install.md). If you want to reset to the same release of the PlanktoScope as what you were originally using, you can check the release's version number in the "Software Version" field of the "Information" panel in [the Node-RED dashboard's System Monitoring page](./user-interface.md#system-monitoring); then you should download an SD card image for the corresponding release (as described in the software installation guide). When you re-flash the SD card, it will lose all data and non-default settings mentioned in [the section of this guide on backing up your data & settings](#back-up-your-data-settings).

## Upgrade/downgrade the PlanktoScope OS

Currently, to upgrade or downgrade your PlanktoScope to some other release of the PlanktoScope OS, we recommend flashing a new SD card with an SD card image for that release of the PlanktoScope OS, following the instructions in our [standard software installation guide](../setup/software/standard-install.md) (or, if you are an advanced user doing something weird/interesting, using the [non-standard software installation guide](../setup/software/nonstandard-install.md)). That way, you can always swap back to your previous SD card if needed. If you only have one SD card, you can re-flash that SD card with the SD card image you want to run - but you will lose all your data and settings, unless you previously [backed them up](#back-up-your-data-settings).

### Perform an in-place upgrade/downgrade

Starting with the [v2024.0.0 release](https://github.com/PlanktoScope/PlanktoScope/releases/tag/software%2Fv2024.0.0) of the PlanktoScope OS, certain software upgrades/downgrades can be performed without re-flashing your SD card, by running a `forklift` command on a PlanktoScope [connected to the internet](./networking.md#connect-your-planktoscope-to-the-internet). However, for now we only recommend using this mechanism for testing certain kinds of changes to the PlanktoScope OS (e.g. as described in specific instructions posted on the PlanktoScope Slack for software-testing volunteers), because certain kinds of frequent software changes (namely, changes to [the Node-RED dashboard](../reference/software/architecture/os.md#user-interface) and [the PlanktoScope hardware controller](../reference/software/architecture/os.md#planktoscope-specific-hardware-abstraction), and changes to the installed version of the `forklift` command) are not yet ready to be managed using `forklift`.

!!! warning

    The PlanktoScope OS's support for in-place upgrade/downgrade functionality is still a work in progress. If you are unsure, then you should perform upgrades/downgrades by (re-)flashing your SD card, not by running a `forklift` command.

When an in-place upgrade to a new release is possible, specific instructions and backwards-compatibility information will be mentioned in the GitHub release notes for that release. However, the general pattern will look something like running the following command (from v2024.0.0 of the PlanktoScope OS), where `{version-query}` would be replaced by a Git branch name (e.g. `beta`), tagged version (e.g. `v2024.0.0`), or (potentially-abbreviated) Git commit SHA:

```sh
forklift pallet switch github.com/PlanktoScope/pallet-standard@{version-query}
```

or one of the following commands (from v2025.0.0-alpha.0 of the PlanktoScope OS):

```sh
# for a specific version:
forklift pallet upgrade @{version-query}
# for the latest version available in the most-recently-used version query:
forklift pallet upgrade
```

and then rebooting after that command finishes successfully.

Eventually (i.e. if/when it becomes feasible and safe), we may make it possible for you to turn on automatic upgrade checks, automatic background downloads of available upgrades, or even automatic installation of upgrades; those features will only have any effects on PlanktoScopes connected to the internet. However, even in that scenario some releases (once every few years) will still require you to re-flash your PlanktoScope's SD card with a new SD card image; this is because of the major release cadence of the Raspberry Pi OS, which is used for building PlanktoScope OS SD card images, and which itself is not safe to upgrade in-place.

!!! info

    If you try to use `forklift` to switch to a version (prerelease/branch/commit) of `github.com/PlanktoScope/pallet-standard` or some other Forklift pallet which attempts to deploy a program which cannot start for some reason, then `forklift` will record that failure and automatically revert back to the previously-running pallet/version combination on every subsequent boot, until the next time you attempt to switch/upgrade/downgrade to some version of some pallet.

    Thus, if you find that you attempted to upgrade the PlanktoScope OS using `forklift` but your PlanktoScope automatically returned to the previous installed version of the OS after a reboot, then that means that your PlanktoScope couldn't run the newer version for some reason. Information about this will be reported if you run the command `forklift stage show`.

### Avoid touching `apt`/`apt-get`!

!!! info

    If you don't know what `apt` or `apt-get` refer to, then please skip this section and just remember to avoid running `apt` or `apt-get` commands on your PlanktoScope!

Most of the "interesting" software in the PlanktoScope OS (with Cockpit being a notable exception) is not managed using Raspberry Pi OS's APT package-management system, [for various reasons](../reference/software/architecture/os.md#system-upgrades). It's *probably* safe to run APT commands to upgrade most packages installed in the PlanktoScope OS (at least for software which doesn't run during [early boot](../reference/software/architecture/os.md#boot-sequence), because of when the PlanktoScope OS's [filesystem overlay](../reference/software/architecture/os.md#filesystem) for `/usr` is initialized), but we cannot make any guarantees or provide any support if you choose to do that. This is an issue of practicality: APT does not make it easy for us to exactly reproduce the changes to installed versions of packages caused by running `apt`/`apt-get`'s install/upgrade commands, when those commands are run at very different times; so it is not necessarily feasible for us to troubleshoot any resulting problems. If you want to undo the changes caused by running any APT commands, you should try to delete everything in `/var/lib/overlays/overrides/usr` and reboot immediately afterwards.

## Restore your data & settings

If you reset/upgraded/downgraded the PlanktoScope OS by re-flashing your SD card, then:

- You can restore your [backed-up data & settings](#back-up-your-data-settings) by re-uploading your backup files to their respective locations and then rebooting your PlanktoScope.
- (Only relevant for advanced users) If you were running a non-standard Forklift pallet (i.e. anything other than [github.com/PlanktoScope/pallet-standard](https://github.com/PlanktoScope/pallet-standard)) which you had pushed to a GitHub repository host (such as GitHub), then you can run a Forklift command to switch back to that pallet (assuming that your PlanktoScope [has an internet connection](./networking.md#connect-your-planktoscope-to-the-internet) so that it can download the pallet), for example in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> :

    ```sh
    forklift pallet switch github.com/name-of/your-pallet@version-query
    ```

    Afterwards, you should reboot your PlanktoScope; it will try to boot using the pallet you had specified.
