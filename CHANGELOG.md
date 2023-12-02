# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Calendar Versioning](https://calver.org/) with a `YYYY.MM.patch` scheme.
All dates in this file are given in the [UTC time zone](https://en.wikipedia.org/wiki/Coordinated_Universal_Time).

## Unreleased

## v2023.9.0-beta.2 - 2023-12-02

### Added

- A `hardware.json` file is now provided for the PlanktoScope v2.6 hardware.

### Removed

- Morphocut is no longer required by the segmenter as a Python package dependency.

### Fixed

- The default brightness of the illumination LED for the pscopehat version of the backend (for the custom PlanktoScope HAT) has been reduced; this a temporary workaround to a bug with raspimjpeg where saved images are overexposed even on the default brightness settings with minimum shutter speed and ISO, despite the brightness of raspimjpeg's camera preview looking reasonable (see https://github.com/PlanktoScope/PlanktoScope/issues/259 for details).

## v2023.9.0-beta.1 - 2023-09-14

### Changed

- The machine name has been switched to the new naming scheme provided by https://github.com/PlanktoScope/machine-name ; the machine name is loaded from a file (currently at `/home/pi/.local/etc/machine-name`, which must be automatically generaed by the host operating system) instead of being determined in Python.

### Deprecated

- The old "Baba"-based machine naming scheme should no longer be used. The `uuidName` module will be removed the next stable release (the stable release after v2023.9.0).

### Fixed

- All default settings for all hardware versions now include a default pixel size calibration of 0.75 um/pixel. Previously, the default settings for v2.1 and v2.3 were missing this setting, which would cause the segmenter to crash when processing datasets generated on PlanktoScopes using the v2.1 or v2.3 hardware settings.

## v2023.9.0-beta.0 - 2023-09-02

### Changed

- Split the Python backend into a hardware controller (of which there are two versions for the Adafruit HAT and the custom PlanktoScope HAT, respectively) and a data processing segmenter. These two components are run separately, and their dependencies are managed separately.
- Each component of the backend now saves its file logs to its respective folder in `/home/pi/device-backend`.

### Fixed

- The default `hardware.json` file for PlanktoScope v2.1 had incorrect keys for the white balance values; the keys have now been fixed.
