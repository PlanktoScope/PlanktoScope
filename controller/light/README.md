# controller.light

The PlanktoScope's hardware controller for the led.

## Usage

### Development

Install all dependencies including development tooling:

```sh
cd light
just
```

Start controller for development:

```sh
cd light
just dev
# make changes and restart
```

### API

### Turn the led on:

**topic** `light`

**payload:**
```json
{
  "action": "on",
  "value": 0.5,
}
```

`value` is a float >= `0` <= `1` that will adjust the led intensity. The default is `1`.

### Turn the led off:

**topic** `light`

**payload:**
```json
{
  "action": "off",
}
```

Turning the led off will trigger incrementing the operating time of the LED in EEPROM.

### status

**topic** `status/light`

**payload when on:**
```json
{
  "action": "On",
  "value": 0.5,
}
```

**payload when off:**
```json
{
  "action": "Off",
}
```

The status will be automatically published to new subscribers.

### status operating time

For now this is implemented in `../../backend/src/led-operating-time.js`.

**topic** `status/led-operating-time`

**payload when on:**
```json
{
  "seconds": 60,
}
```

`seconds` is an integer representing the number of seconds the LED was on.

The led-operating-time will be automatically published to new subscribers.

It is updated when the light turns off.

### reset operating time

For now this is implemented in `../../backend/src/led-operating-time.js`.

**topic** `led-operating-time`

**payload:**
```json
{
  "action": "reset",
}
```

This will reset the operating time of the LED to 0 seconds. Useful when changing the LED.
