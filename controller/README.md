# Controller

The PlanktoScope's hardware controller.

## Architecture

Each feature of the hardware is controlled by a separate process. Processes communicate between each other and with external clients using MQTT.

Please note the following particularity of Python processes

> Bear in mind that each spawned process is initialized with a copy of the memory footprint of the master process. And that the constructor code (i.e. stuff inside **init**()) is executed in the master process -- only code inside run() executes in separate processes.

https://stackoverflow.com/a/17220739

## Usage

### Development

Install all dependencies including development tooling:

```sh
cd controller
just
```

Start controller for development:

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

We recommand using [https://code.visualstudio.com/docs/remote/ssh](https://code.visualstudio.com/docs/remote/ssh)

## Licensing

Except where otherwise indicated, source code provided here is covered by the following information:

Copyright PlanktoScope project contributors

SPDX-License-Identifier: GPL-3.0-or-later

You can use the source code provided here under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
