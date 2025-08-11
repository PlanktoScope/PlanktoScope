```sh
eepmake eeprom_settings.txt planktoscope-hat.eep

# write
sudo gpioset -m signal gpiochip0 26=0 # disable write protect
sudo eepflash.sh --yes --write --type=24c32 --address=50 --file=planktoscope-hat.eep
ee

# read
sudo eepflash.sh --yes --read --type=24c32 --address=50 --file=dump.eep
eepdump dump.eep
```

See https://github.com/raspberrypi/utils/blob/master/eeptools/eeprom_settings.txt
