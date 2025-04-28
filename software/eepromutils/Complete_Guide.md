# Complete guide for the HAT Eeprom
Retrieved and adapted from https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=108134 on 2021-07-12


First of all, you need to install the device-tree compiler (dtc). The compiler should be available from your OS packages repositories. The other needed tools are available in this folder as source code. They will be compiled automagically when needed.

# eeprom_settings.txt
Your first step is to check or modify eeprom_settings.txt to make it fit to your hardware configuration. You don't have to modify UUID, as it will be auto-generated. The settings should have already been made in this repository.

Then, you can create and flahs an eep file, based on you `eeprom_settings.txt` file. Basically, an eep file is a binary version of this file, which is ready to flash on EEPROM.

```
make flash_full_and_check
```

You have now a working HAT eeprom!

This command will first create the compiled eep file (and if needed, compile the tools to do so), generate a 4kB blank eep file (the size of the Hat eeprom), merge the two files together and flash this to the eeprom. Finally, the flash is checked.

Before flashing, you will need to close the Write Protect jumper on the underside of the HAT with a solder blob. This will remove the read-only flag and allow the eeprom to be written on.

If the flash is successfull, you can restart the machine.

To check if your HAT is recognized, just check in `/proc/device-tree/`. If you see a hat directory, you are succesfull!

```
more /proc/device-tree/hat/vendor
more /proc/device-tree/hat/product
```

# Device tree file
The next step is to allow autoconfiguration of this HAT, following device-tree usage. In our example, we have a led connected to GPIO 18 (pin 12). I suggest you to test it before, using /sys/class/gpio :

```
sudo sh -c 'echo "18" > /sys/class/gpio/export'
sudo sh -c 'echo "out" > /sys/class/gpio/gpio18/direction'
sudo sh -c 'echo "1" > /sys/class/gpio/gpio18/value'
```

Your led is powered on. And to power off :

```
sudo sh -c 'echo "0" > /sys/class/gpio/gpio18/value'
```

Now we can dive in the device-tree world. Open and edit the file `pscope_hat.dts` as needed:

```
/dts-v1/;
/plugin/;

/ {
    compatible = "brcm,bcm2708";

    fragment@0 {
        target = <&leds>;
        __overlay__ {
            my_led: myled {
                label = "MYLED";
                gpios = <&gpio 18 0>;
                linux,default-trigger = "heartbeat";
            };
        };
    };
};
```

Compile it with dtc compiler :

```
make dtb
```

For testing purposes, you can load this dtb as an overlay, using `dtoverlay=` in `/boot/firmware/config.txt`. Don't forget to copy the `pscope_hat.dtb` file to your `/boot/overlays` folder.

Now, we can generate a eep file containing both board definition (eeprom_config.txt) and device-tree (for kernel auto configuration).

```
make flash_complete_and_check
```

Finally, do a reboot, and enjoy your working PlanktoScope HAT!


Final reminder: When you start playing with adding long device tree, keep in mind you have a limited memory (4096 bytes for a 24c32 memory). When creating an eep file with eepmake, this tool will give you final size of your eep. Just verifiy if you have exceed your EEPROM size.

Note: With an incorrect DT, even your eeprom_settings are not recognized by kernel. And a bootable device-tree overlay is sometimes not sufficient for "eeprom boot"

To allow auto configuration after kernel boot (ie: modprobe some modules, TFT calibration, etc...), I use a custom parameter file, based on JSON, that could be parsed after. I choose JSON as it is small, human-readable, and easy to parse.
To add a custom file to your eep, just do this:

```
./eepmake eeprom_settings.txt myhat-with-dt.eep myled.dtb -c myparams.json
```
