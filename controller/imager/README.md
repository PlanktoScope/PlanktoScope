# controller.imager

The PlanktoScope's imager

This is both:

* hardware controller for the camera
* pump/picture scheduler (see [`stopflow.py`](./stopflow.py))

## Usage

### Development

Install all dependencies including development tooling:

```sh
cd imager
just
```

Start controller for development:

```sh
cd imager
just dev
# make changes and restart
```
