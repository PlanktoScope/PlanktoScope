# EEPROM

API and service for the PlanktoScope HAT EEPROM.

See https://github.com/raspberrypi/utils/blob/master/eeptools

### Development

Install all dependencies including development tooling:

```sh
cd eeprom
just
```

Start service for development:

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

## Notes

```sh
eepmake eeprom_settings.txt planktoscope-hat.eep

# write
sudo gpioset -m signal gpiochip0 26=0 # disable write protect
sudo eepflash.sh --yes --write --type=24c32 --address=50 --file=planktoscope-hat.eep
ee

# read
sudo eepflash.sh --yes --read --type=24c32 --address=50 --file=dump.eep
eepdump dump.eep dump.txt
```
