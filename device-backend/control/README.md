# control

The PlanktoScope's hardware controller.

Note: this is a work-in-progress refactor and is not yet ready for general use.

## Introduction

This repository contains the PlanktoScope's hardware controller, which controls the PlanktoScope's sensors and actuators, producing raw data. Currently, device control consists of:
- Hardware abstraction layers: implements a simple, mostly-uniform internal API on different underlying hardware devices, for the application-level hardware controller to be used with different hardware implementations of PlanktoScope designs.
- Application-level controller: provides device behaviors (such as stop-flow imaging) generalizable across different generations of PlanktoScopes. In software engineering jargon, this is the "business logic" of the PlanktoScope hardware-control software.
- API adapter: exposes the application-level controller with a standard public API for other software clients to use.

However, the organization of the source code does not yet reflect the organization of software functionalities.

## Usage

### Deployment

Currently the hardware controller can only be deployed as part of the distro setup scripts at [github.com/PlanktoScope/PlanktoScope](https://github.com/PlanktoScope/PlanktoScope).

Please note that for camera we rely on the Raspberry OS packages `python3-picamera2` and `python3-libcamera`.

### Development

To install all dependencies including development tooling, run:
```
poetry install --with dev --no-root
```

Then you can run the code auto-formatter on the project by running:
```
poetry run poe fmt
```

And you can run all checks (including code formatting and linting) by running:
```
poetry run poe check
```

If you'd like to copy your files to a remote PlanktoScope, you can run:
```
HOST=pkscope.local poetry run poe scp
```
from the directory which contains this readme. This command will overwrite existing files in
`/home/pi/device-backend/control`, but it will not delete any files or directories which you might
have deleted from your computer's local copy of this directory. Note that this command requires that
you have a `scp` command (so you probably need to be running on Linux or macOS, or on Windows
Subsystem for Linux). And you can change `pkscope.local` to something else (e.g. `home.pkscope`) if
needed.

### Prerequisites

To use this project, you'll need:

- Python >= 3.9
- Poetry 2.1.2

## Licensing

Except where otherwise indicated, source code provided here is covered by the following information:

Copyright PlanktoScope project contributors

SPDX-License-Identifier: GPL-3.0-or-later

You can use the source code provided here under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
