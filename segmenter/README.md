# segmenter

The PlanktoScope's segmenter.

## Introduction

This repository contains the PlanktoScope's segmenter, which detects objects from camera frames and creates an image for each isolated object, with the background removed.

## Usage

### Deployment

The segmenter is published for deployment as a Docker container image at [https://ghcr.io/PlanktoScope/segmenter](https://github.com/PlanktoScope/PlanktoScope/pkgs/container/segmenter). Note that the segmenter requires an MQTT broker accessible on the port 1883 of the host, as well as something to send MQTT commands to the segmenter.

### Development

Install all dependencies including development tooling:

```sh
cd controller
just
```

Start segmenter for development:

```sh
just dev
# make changes and restart
```

Run the code auto-formatter on the project:

```sh
just format
```

Run all checks (including code formatting and linting):

```sh
just test
```

We recommand using [VSCode SSH](https://code.visualstudio.com/docs/remote/ssh)

### Prerequisites

To use this project, you'll need:

- Python >= 3.13.5
- Poetry 2.1.3

## Licensing

Except where otherwise indicated, source code provided here is covered by the following information:

Copyright PlanktoScope project contributors

SPDX-License-Identifier: GPL-3.0-or-later

You can use the source code provided here under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
