# Product Specifications

Product specifications for the PlanktoScope software are listed below for ranges of software version numbers. To see software versions listed individually in chronological order, refer to the [project release notes](https://github.com/PlanktoScope/PlanktoScope/releases) or the [software changelog](./changelog.md).

## v2023.9.0 - v2024.0.0

### Functionalities

Regular operation:

- Image acquisition: stop-flow imaging
- On-board image processing: detection and segmentation of objects (batch-processing only)
- User interfacing: graphical interface accessible through web browser of a connected phone, tablet, or computer

Advanced operations:

- User interfacing: web browser interfaces for system administration, system monitoring, and troubleshooting
- Automation: MQTT-based API
- Application deployment: ability to add software as OCI containers using Docker

### Base operating system

- Distro: Raspberry Pi OS 11 (bullseye)
- Binary target architecture: 32-bit only (armhf, also known as armv7)

### Supported hardware

Minimum for image acquisition (but not sufficient for on-board image processing):

- PlanktoScope: hardware v2.1 with Raspberry Pi 4 Model B computer
- Memory: 1 GB RAM
- Storage: 8 GB capacity

Minimum for full functionality, including on-board image processing:

- Memory: 4 GB RAM

Recommended:

- PlanktoScope: hardware v2.5 or v2.6 with Raspberry Pi 4 Model B computer
- Storage: 32 GB capacity

Forwards-incompatibilities:

- These software versions are unable to run on the Raspberry Pi 5 computer.

Backwards-incompatibilities:

- These software versions might still work on a Raspberry Pi 3 Model B+ computer or a Raspberry Pi 4 Model B computer with 1 GB of RAM, but compatibility is not tested.

### System performance

With minimum supported hardware for full functionality:

- On-board image processing: a dataset of 400 raw images is processed in approximately 1.5 to 2 hours

## v2.3

### Functionalities

Regular operation:

- Image acquisition: stop-flow imaging
- On-board image processing: detection and segmentation of objects (batch-processing only)
- User interfacing: graphical interface accessible through web browser of a connected phone, tablet, or computer

Advanced operations:

- Automation: MQTT-based API

### Base operating system

- Distro: Raspberry Pi OS 11 (bullseye)
- Binary target architecture: 32-bit only (armhf, also known as armv7)

### Supported hardware

Minimum for image acquisition (but not sufficient for on-board image processing):

- PlanktoScope: hardware v2.1 with Raspberry Pi 3 Model B+ computer
- Memory: 1 GB RAM
- Storage: 8 GB capacity

Minimum for full functionality, including on-board image processing:

- PlanktoScope: hardware v2.1 with Raspberry Pi 4 Model B computer
- Memory: 4 GB RAM

Recommended for full functionality:

- PlanktoScope: hardware v2.5 or v2.6
- Storage: 32 GB capacity

Forwards-incompatibilities:

- This software version is unable to run on the Raspberry Pi 5 computer.
- This software version is incompatible with Adafruit Stepper Motor HATs (used in PlanktoScope hardware v2.1) manufactured after mid-2022.

### System performance

With minimum supported hardware for full functionality:

- On-board image processing: a dataset of 400 raw images is processed in approximately 1.5 to 2 hours
