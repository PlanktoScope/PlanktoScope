# controller.display

The PlanktoScope's hardware controller for the display.

## Usage

### Development

Install all dependencies including development tooling:

```sh
cd display
just
```

Start controller for development:

```sh
cd display
just dev
# make changes and restart
```

The controller does nothing by default, you can use

```sh
cd pump
node test.js
```

while the controller is started to trigger the display.

### API

### Configure the display:

**topic** `display`

**payload:**
```json
{
  "action": "configure",
  "config": {
    "url": "http://...",
    "online": false,
  }
}
```
