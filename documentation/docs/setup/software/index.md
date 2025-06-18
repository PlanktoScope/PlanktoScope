# PlanktoScope Software

This section of the PlanktoScope documentation will help you to set up the necessary software for your PlanktoScope hardware. Our documentation splits the PlanktoScope software setup process into two phases: installing the PlanktoScope software onto the micro-SD card of the Raspberry Pi computer in your PlanktoScope, and configuring the PlanktoScope software after installation.

The PlanktoScope software is an operating system, the [PlanktoScope OS](../../reference/software/architecture/os.md), distributed as an SD card image to be run on the PlanktoScope hardware's embedded Raspberry Pi computer.

If you are building your own PlanktoScope from your own hardware kit, you will need to install and set up the PlanktoScope OS yourself. If you received a PlanktoScope from FairScope, a working and pre-configured version of the PlanktoScope OS is already pre-installed, and you can skip the software setup process and proceed to our guide on how to [operate your PlanktoScope](../../operation/index.md). - but you still might wish to update your PlanktoScope to the latest release of the PlanktoScope OS, in which case you should reinstall the PlanktoScope software by going through our software setup guide below.

In order to install the PlanktoScope software, you will first need to choose an SD card image file to use for installation, and then you will install that SD card image and perform some configuration of the software.

### PlanktoScope OS versions

Because the PlanktoScope project aims to release occasional updates to the PlanktoScope OS in order to fix various software problems and make various improvements to the software, multiple versions of the PlanktoScope OS exist, and new versions will be released in the future. In general, each version of the PlanktoScope OS will be compatible with all previous officially-released versions of the PlanktoScope hardware (which are all versions listed in the [hardware changelog](../../reference/hardware/changelog.md) without the description of a "prototype"). The PlanktoScope documentation describes the latest stable release of the PlanktoScope OS, and you should always use the latest stable release on your PlanktoScopes.

PlanktoScope OS versions are independent of hardware versions, and (starting in 2023) use a different version numbering system from the hardware (see the [Hardware setup guide](../hardware/index.md#hardware-versions) for an overview of some hardware versions). Now, OS version numbers have three numeric components: the year of the release, a minor number (which is incremented for releases with new features and/or backwards-incompatible changes), and a patch number (which is incremented for minor bugfixes). You may see references to the following SD card image versions in online discussions of the PlanktoScope software:

- v2.3: this release, from December 2021, was the last release of the PlanktoScope software in the old version numbering system in which the software and hardware were released together. The v2.3 OS is preinstalled on most PlanktoScopes sold by FairScope during 2023.

- v2023.9.0: this release, from the end of 2023, is the first software release in the new version numbering system, and it is currently the latest release of the PlanktoScope OS. The number `9` should not be interpreted as having any special meaning.

- v2024.0.0: this version is the first release of the PlanktoScope OS in 2024.

- v2024.1.0: this version will be the second release of the PlanktoScope OS in 2024.

## Installation

After you have chosen a PlanktoScope OS SD card image for the desired OS version and hardware configuration, you should follow our [standard installation](standard-install.md) guide in order to install that SD card image into your PlanktoScope.

## Post-installation configuration

The first time you start the PlanktoScope after installing or updating the software, you should change some settings in the PlanktoScope software in order to match the configuration of your PlanktoScope hardware. Refer to our [post-installation configuration](config.md) guide for details.

## Next steps

After [installing](standard-install.md) the PlanktoScope software (or after ensuring that the PlanktoScope software is installed) and performing all necessary [post-installation configuration](config.md), then you can proceed to our guide on how to [operate your PlanktoScope](../../operation/index.md).
