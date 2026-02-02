# Controller

The PlanktoScope's hardware controller.

## Architecture

Each feature of the hardware is controlled by a separate process. Processes communicate between each other and with external clients using MQTT.

* [bubbler](./bubbler)
* [display](./display)
* [focus](./focus)
* [imager](./imager)
* [light](./light)
* [pump](./pump)

## Usage

### Development

Install all dependencies including development tooling:

```sh
cd controller
just setup setup-dev
```

Run the code auto-formatter on the project:

```sh
just format
```

Run all checks (including code formatting and linting):

```sh
just test
```

## Licensing

Except where otherwise indicated, source code provided here is covered by the following information:

Copyright PlanktoScope project contributors

SPDX-License-Identifier: GPL-3.0-or-later

You can use the source code provided here under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
