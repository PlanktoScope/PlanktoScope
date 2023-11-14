# PlanktoScope Software

This section of the PlanktoScope documentation will help you to set up the necessary software for your PlanktoScope hardware. Our documentation splits this PlanktoScope production process into two phases: installing the PlanktoScope software onto the micro-SD card of the Raspberry Pi computer in your PlanktoScope, and configuring the PlanktoScope software after installation.

The PlanktoScope software is distributed as an SD card image to be run on the PlanktoScope hardware's embedded Raspberry Pi computer. The PlanktoScope SD card image provides a ready-to-use collection of software programs for operating and managing the PlanktoScope from the web browser of a computer or phone connected to the PlanktoScope - so we also use the terms "PlanktoScope [software distribution](https://en.wikipedia.org/wiki/Software_distribution)" and "PlanktoScope distro" to refer to the PlanktoScope software when we provide it as an integrated collection of software components (e.g. an SD card image).

If you are building your own PlanktoScope from your own hardware kit, you will need to install the PlanktoScope software. If you received a PlanktoScope from FairScope, a working version of the PlanktoScope software is already pre-installed, and you can skip to the [post-installation configuration](#post-installation-configuration) section of this page - but you still might wish to update the software to the latest release of the PlanktoScope distro, in which case you should reinstall the PlanktoScope software. In order to install the PlanktoScope software, you will first need to choose an SD card image file to use for installation.

## Choosing an SD card image

PlanktoScope SD card image files are identified with a version number as well as a hardware configuration tag - for example, the SD card image file named `planktoscope-v2023.9.0+pscopehat.img.gz` is for v2023.9.0 of the PlanktoScope distro, configured to work with versions of the PlanktoScope hardware based on the custom PlanktoScope HAT (rather than the Adafruit Stepper Motor HAT). Thus, you will need to choose both a version number (e.g. v2023.9.0) and a hardware configuration (e.g. `pscopehat`).

### Distro versions

Because the PlanktoScope project aims to release occasional updates to the PlanktoScope distro in order to fix software problems and make the software easier to operate, multiple versions of the PlanktoScope distro exist, and new distro versions will be released in the future. In general, each version of the PlanktoScope distro will be compatible with all previous officially-released versions of the PlanktoScope hardware (which are the versions listed in the [hardware changelog](../../reference/hardware/changelog.md) without the description of a "prototype"). The PlanktoScope documentation describes the latest stable release of the PlanktoScope distro, and you should always use the latest stable release on your PlanktoScopes.

PlanktoScope distro versions are independent of hardware versions, and (starting in 2023) use a different version numbering system from the hardware (see the [Hardware setup guide](../hardware/index.md#hardware-versions) for an overview of some hardware versions). Now, distro version numbers have three numbers: the year of the release, a minor number (which is incremented for releases with new features and/or backwards-incompatible changes), and a patch number (which is incremented for minor bugfixes). You may see references to the following SD card image versions in online discussions of the PlanktoScope software:

- v2.3: this release, from December 2021, was the last release of the PlanktoScope software in the old version numbering system in which the software and hardware were released together. The v2.3 distro is preinstalled on most PlanktoScopes sold by FairScope during 2023.

- v2023.9.0: this release, from the end of 2023, is the first software release in the new version numbering system, and it is currently the latest release of the PlanktoScope distro. The number `9` should not be interpreted as having any special meaning.

- v2024.0.0: this version will be the first release of the PlanktoScope distro in 2024.

### Hardware configurations

Currently, each version of the PlanktoScope distro is provided as two SD card images, corresponding to the two different hardware configurations supported by the PlanktoScope software:

- `adafruithat`: this configuration of the PlanktoScope distro is compatible with v2.1 of the PlanktoScope hardware, which uses the Adafruit Stepper Motor HAT.

- `pscopehat`: this configuration of the PlanktoScope distro is compatible with all versions of the PlanktoScope hardware starting with hardware v2.3; those hardware versions use a custom HAT.

If you have a v2.1 PlanktoScope, you should probably use an `adafruithat` SD card image; if you have a PlanktoScope from FairScope or any hardware version after v2.3, you should probably use the `pscopehat` SD card image.

## Installation

After you have chosen a PlanktoScope SD card image for the desired software version and hardware configuration, you should follow our [standard installation](standard-install.md) guide in order to install that SD card image into your PlanktoScope. If the official PlanktoScope SD card images don't meet your requirements and you have successfully set up and used the PlanktoScope software in the past via the standard installation process, then you may also find the [non-standard installation](nonstandard-install.md) guide useful.

## Post-installation configuration

The first time you start the PlanktoScope after installing or updating the software, you should change some settings in the PlanktoScope software in order to match the configuration of your PlanktoScope hardware. Refer to our [post-installation configuration](config.md) guide for details.

## Next steps

After you have ensured that the PlanktoScope software is installed in your PlanktoScope, and you have performed any necessary post-installation configuration, then you can proceed to our guide on how to [operate your PlanktoScope](../../operation/index.md).
