# Controller

The PlanktoScope's hardware controller.

## Architecture

Each feature of the hardware is controlled by a separate process. Processes communicate between each other and with external clients using MQTT.

Please note the following particularity of Python processes

> Bear in mind that each spawned process is initialized with a copy of the memory footprint of the master process. And that the constructor code (i.e. stuff inside **init**()) is executed in the master process -- only code inside run() executes in separate processes.

https://stackoverflow.com/a/17220739

## Usage

### Deployment

Currently the hardware controller can only be deployed as part of the distro setup scripts at [github.com/PlanktoScope/PlanktoScope](https://github.com/PlanktoScope/PlanktoScope).

Please note that for camera we rely on the Raspberry OS packages `python3-picamera2` and `python3-libcamera`.

### Development

Install all dependencies including development tooling:

```sh
poetry install --with dev
```

Start controller for development:

```sh
sudo systemctl stop planktoscope-org.controller.service
poetry run python -u main.py
# make changes and restart
```

Run the code auto-formatter on the project:

```sh
poetry run poe fmt
```

Run all checks (including code formatting and linting):

```sh
poetry run poe check
```

We recommand using [https://code.visualstudio.com/docs/remote/ssh](https://code.visualstudio.com/docs/remote/ssh)

### Prerequisites

To use this project, you'll need:

- Python >= 3.11.2
- Poetry 2.1.3

## Licensing

Except where otherwise indicated, source code provided here is covered by the following information:

Copyright PlanktoScope project contributors

SPDX-License-Identifier: GPL-3.0-or-later

You can use the source code provided here under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
