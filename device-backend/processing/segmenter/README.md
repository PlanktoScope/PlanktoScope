# segmenter

The PlanktoScope's segmenter.

## Introduction

This repository contains the PlanktoScope's segmenter, which detects objects from camera frames and creates an image for each isolated object, with the background removed.

## Usage

### Deployment

The segmenter is published for deployment as a Docker container image at [https://ghcr.io/PlanktoScope/device-backend-processing-segmenter](https://github.com/PlanktoScope/device-backend/pkgs/container/device-backend-processing-segmenter). Note that the segmenter requires an MQTT broker accessible on the port 1883 of the host, as well as something to send MQTT commands to the segmenter.

Currently, the simplest way to deploy the segmenter on any computer is using the [Forklift](https://github.com/PlanktoScope/forklift) pallet [github.com/PlanktoScope/pallet-segmenter](https://github.com/PlanktoScope/pallet-segmenter). However, that method is still experimental.

### Development

TBD

### Prerequisites

To use this project, you'll need:

- Python >= 3.11.2
- Poetry 2.1.2

## Licensing

Except where otherwise indicated, source code provided here is covered by the following information:

Copyright PlanktoScope project contributors

SPDX-License-Identifier: GPL-3.0-or-later

You can use the source code provided here under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
