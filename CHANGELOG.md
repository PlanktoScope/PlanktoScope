# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Calendar Versioning](https://calver.org/) with a `YYYY.MM.patch` scheme
for all releases after `v2.3.0`.
All dates in this file are given in the [UTC time zone](https://en.wikipedia.org/wiki/Coordinated_Universal_Time).

## Unreleased

### Changed

- Split the Python backend into a hardware controller (of which there are two versions for the Adafruit HAT and the custom PlanktoScope HAT, respectively) and a data processing segmenter. These two components are run separately, and their dependencies are managed separately.
- Each component of the backend now saves its file logs to its respective folder in `/home/pi/device-backend`.

### Fixed

- The default `hardware.json` file for PlanktoScope v2.1 had incorrect keys for the white balance values; the keys have now been fixed.
