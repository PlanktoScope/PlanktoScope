# controller.focus

The PlanktoScope's hardware controller for the focus.

## Usage

### Development

Install all dependencies including development tooling:

```sh
cd focus
just
```

Start controller for development:

```sh
cd focus
just dev
# make changes and restart
```

### API

### Start the focus:

**topic** `actuator/focus`

**payload:**
```json
{
  "action": "focus",
  "direction": "UP", // "UP" or "DOWN"
  "distance": 45, // distance to move, in mm
  "speed": 5 // speed of moving, in mm/sec - optional
}
```

### Stop the focus:

**topic** `actuator/focus`

**payload:**
```json
{
  "action": "stop",
}
```

### status

**topic** `status/focus`

**payload when started:**
```json
{
  "status": "Started",
  "duration": 10, // duration in seconds
}
```

**payload when completed:**
```json
{
  "status": "Done",
}
```

**payload when stopped:**
```json
{
  "status": "Interrupted",
}
```

The status will be automatically published to new subscribers.
