# controller.bubbler

The PlanktoScope's hardware controller for the bubbler.

## Usage

### Development

Install all dependencies including development tooling:

```sh
cd bubbler
just
```

Start controller for development:

```sh
cd bubbler
just dev
# make changes and restart
```

### API

### Start the bubbler:

**topic** `actuator/bubbler`

**payload:**
```json
{
  "action": "on",
}
```

### Stop the bubbler:

**topic** `actuator/bubbler`

**payload:**
```json
{
  "action": "off",
}
```

### status

**topic** `status/bubbler`

**payload when started:**
```json
{
  "status": "On",
}
```

**payload when stopped:**
```json
{
  "status": "Off",
}
```

The status will be automatically published to new subscribers.
