# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Calendar Versioning](https://calver.org/) with a `YYYY.minor.patch` scheme.
All dates in this file are given in the [UTC time zone](https://en.wikipedia.org/wiki/Coordinated_Universal_Time).

## Unreleased

### Changed

- (Breaking change; segmenter) Previously, the segmenter's default behavior was to subtract consecutive masks to try to mitigate image-processing issues with objects which get stuck to the flowcell during imaging. However, when different objects occupied the same space in consecutive frames, the subtraction behavior would subtract one object's mask from the mask of the other object in the following frame, which would produce clearly incorrect masks. This behavior is no longer enabled by default; in order to re-enable it, you should set the environment variable `SEGMENTER_PIPELINE_SUBTRACT_CONSECUTIVE_MASKS=true` when launching the segmenter.
- (Hardware controller) The image quality of frames in the camera preview stream for the picamera2-based imager is increased, and frames also have greater width and height.

### Deprecated

- (Hardware controller) The old raspimjpeg-based imager is deprecated and will be fully deleted in a subsequent release (potentially as early as v2024.1.0).

### Fixed

- (Hardware controller) The incorrect scaling factor for converting between ISO settings (in the MQTT API) and image gains is fixed.

## v2024.0.0-alpha.1 - 2024-03-26

### Added

- (Hardware controller) A new picamera2-based camera-management module (`camera`) is now available as an alternative to the camera-management part of the previous raspimjpeg-based image-acquisition-and-camera-management module.
- (Hardware controller) A new image-acquisition module (`imagernew`) is now available for use with the new picamera2-based `camera` module, as an alternative to the image-acquisition part of the previous raspimjpeg-based image-acquisition-and-camera-management module.

### Changed

- (Hardware controller) The new picamera2-based image-acquisition module (`imagernew`) is now used by default, instead of the previous raspimjpeg-based `imager` module.
- (Breaking change; segmenter) EcoTaxa export archive filenames are now saved as `ecotaxa_{acquisition id}.zip` instead of `ecotaxa_{project id}_{date}_{sample id}.zip`, which was long and redundant and (because many devices have incorrect system times) inappropriate for viewing files in a logically sorted order.
- (Breaking change; hardware controller) The version of the hardware controller for the PlanktoScope HAT has been moved from `control/pscopehat` to `control/planktoscopehat`.

### Fixed

- (Breaking change; hardware controller) Images acquired by the hardware controller using the newly-default `imagernew` image-acquisition module now have more unique filenames (which include an incrementing index and the date of image capture, rather than just the time of the image capture).
- (Hardware controller) The hardware controller using the newly-default `imagernew` image-acquisition module no longer crashes when invalid values are given for camera settings (e.g. null or non-numeric white balance gains).
- (Hardware controller) The pixel calibration values have been switched between the default v2.5 hardware config file and the default v2.6 hardware config file, so that each file has the correct pixel calibration. The default pscopehat hardware config file has also been updated to include the changes made to the default v2.6 hardware config file.
- (Breaking change; segmenter) The segmenter now runs as `root` (instead of `pi`) in the Docker container for it, so that it doesn't break on various actual & potential edge cases of files/directories being created with `root` ownership (rather than `pi` ownership) before being bind mounted into the container.

## v2024.0.0-alpha.0 - 2024-02-06

### Added

- (Segmenter) A Docker container image is now built for the segmenter, for amd64, arm64, and armv7.

### Changed

- (Breaking change) The machine name is now loaded from `/var/lib/planktoscope/machine-name`, rather than the previous location of `/home/pi/.local/etc/machine-name`.

### Fixed

- (Segmenter) An extraneous `export` directory should no longer be created by the segmenter under `/home/pi/PlanktoScope`. The correct directory is `/home/pi/data/export`.

## v2023.9.0 - 2023-12-29

(this release involves no changes from v2023.9.0-beta.2; it's just a version bump)

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
