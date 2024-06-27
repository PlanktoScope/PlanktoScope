# Product Specifications

The PlanktoScope OS includes all software which needs to run on the PlanktoScope's hardware to provide the [overall functionality of a PlanktoScope](../index.md). Product specifications for the PlanktoScope OS are listed below for ranges of software version numbers. To see software versions listed individually in chronological order, refer to the [project release notes](https://github.com/PlanktoScope/PlanktoScope/releases) or the [software changelog](./changelog.md). To understand how to interpret software version numbers, refer to our description of the PlanktoScope OS's [version numbering system](./release-process.md#version-numbering).

## v2024.0.0

Specs for v2024.0.0 are the same as in v2023.9.0, except for the following sections:

- Base operating system: the binary target architecture has changed from 32-bit to 64-bit.
- System performance: on-board image processing speeds have improved (processing speeds have nearly doubled).

### Functionalities

Regular operation:

- Image acquisition: stop-flow imaging (JPEG image output)
- On-board image processing: detection and segmentation of objects (batch-processing only)
- User interfacing: graphical interface accessible through web browser of a connected phone, tablet, or computer
- Export of data for uploading to EcoTaxa

Advanced operations:

- User interfacing: web browser interfaces for system administration, system monitoring, and troubleshooting
- Automation: MQTT-based API
- Application deployment: ability to add software as OCI containers using Docker, optionally via [Forklift](https://docs-edge.planktoscope.community/reference/software/architecture/os/#package-management-with-forklift)
- System configuration: ability to reversibly add, remove, replace, or override OS configuration files via Forklift

### Base operating system

- Distro: Raspberry Pi OS 11 (bullseye)
- Binary target architecture: 64-bit (aarch64, also known as arm64)

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

- Unable to run on the Raspberry Pi 5 computer.

Backwards-incompatibilities:

- Might still work on a Raspberry Pi 3 Model B+ computer or a Raspberry Pi 4 Model B computer with 1 GB of RAM, but compatibility is not tested.

### System performance

With minimum supported hardware for full functionality:

- On-board image processing: a dataset of 400 raw images is processed in approximately 1 hour

## v2023.9.0

### Functionalities

Regular operation:

- Image acquisition: stop-flow imaging (JPEG image output)
- On-board image processing: detection and segmentation of objects (batch-processing only)
- User interfacing: graphical interface accessible through web browser of a connected phone, tablet, or computer
- Export of data for uploading to EcoTaxa

Advanced operations:

- User interfacing: web browser interfaces for system administration, system monitoring, and troubleshooting
- Automation: MQTT-based API
- Application deployment: ability to add software as OCI containers using Docker, optionally via [Forklift](https://docs-edge.planktoscope.community/reference/software/architecture/os/#package-management-with-forklift)

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

- Unable to run on the Raspberry Pi 5 computer.

Backwards-incompatibilities:

- Might still work on a Raspberry Pi 3 Model B+ computer or a Raspberry Pi 4 Model B computer with 1 GB of RAM, but compatibility is not tested.

### System performance

With minimum supported hardware for full functionality:

- On-board image processing: a dataset of 400 raw images is processed in approximately 1.5 to 2 hours

## v2.3

### Functionalities

Regular operation:

- Image acquisition: stop-flow imaging (JPEG image output)
- On-board image processing: detection and segmentation of objects (batch-processing only)
- User interfacing: graphical interface accessible through web browser of a connected phone, tablet, or computer
- Export of data for uploading to EcoTaxa

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

- Unable to run on the Raspberry Pi 5 computer.
- Incompatible with Adafruit Stepper Motor HATs (used in PlanktoScope hardware v2.1) manufactured after mid-2022.

### System performance

With minimum supported hardware for full functionality:

- On-board image processing: a dataset of 400 raw images is processed in approximately 1.5 to 2 hours
