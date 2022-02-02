# Using a flash with the camera

The Pi's camera module includes an LED flash driver which can be used to illuminate a scene upon capture. The flash driver has two configurable GPIO pins:

* one for connection to an LED based flash (xenon flashes won't work with the camera module due to it having a `rolling shutter`). This will fire before (`flash metering`) and during capture
* one for an optional privacy indicator (a requirement for cameras in some jurisdictions). This will fire after taking a picture to indicate that the
  camera has been used

These pins are configured by updating the `VideoCore device tree blob`. Firstly, install the device tree compiler, then grab a copy of the default
device tree source:
```
$ sudo apt-get install device-tree-compiler
$ wget https://github.com/raspberrypi/firmware/raw/master/extra/dt-blob.dts
```

The device tree source contains a number of sections enclosed in curly braces, which form a hierarchy of definitions. The section to edit will depend on which revision of Raspberry Pi you have (check the silk-screen writing on the board for the revision number if you are unsure):

Model | Section
------|:--------:
Raspberry Pi Model B rev 1 | `/videocore/pins_rev1`
Raspberry Pi Model A and Model B rev 2 | `/videocore/pins_rev2`
Raspberry Pi Model A+ | `/videocore/pins_aplus`
Raspberry Pi Model B+ rev 1.1 | `/videocore/pins_bplus1`
Raspberry Pi Model B+ rev 1.2 | `/videocore/pins_bplus2`
Raspberry Pi 2 Model B rev 1.0 | `/videocore/pins_2b1`
Raspberry Pi 2 Model B rev 1.1-1.2 | `/videocore/pins_2b2`
Raspberry Pi 3 Model B rev 1.0 | `/videocore/pins_3b1`
Raspberry Pi 3 Model B rev 1.2 | `/videocore/pins_3b2`
Raspberry Pi Zero rev 1.2-1.3 | `/videocore/pins_pi0`



Under the section for your particular model of Pi you will find `pin_config` and `pin_defines` sections. Under the `pin_config` section you need to configure the GPIO pins you want to use for the flash and privacy indicator as using pull down termination. Then, under the `pin_defines` section you need to associate those pins with the `FLASH_0_ENABLE` and `FLASH_0_INDICATOR` pins.

For example, to configure GPIO 17 as the flash pin, leaving the privacy indicator pin absent, on a Raspberry Pi 2 Model B rev 1.1 you would add the following line under the `/videocore/pins_2b2/pin_config` section:
```
    pin@p17 { function = "output"; termination = "pull_down"; };
```

Please note that GPIO pins will be numbered according to the `Broadcom pin numbers`(BCM mode in the RPi.GPIO library, *not* BOARD mode). Then change the following section under `/videocore/pins_2b2/pin_defines`. Specifically, change the type from "absent" to "internal", and add a number property defining the flash pin as GPIO 17:

```
    pin_define@FLASH_0_ENABLE {
        type = "internal";
        number = <17>;
    };
```

With the device tree source updated, you now need to compile it into a binary blob for the firmware to read. This is done with the following command line:
```
$ dtc -q -I dts -O dtb dt-blob.dts -o dt-blob.bin
```

Dissecting this command line, the following components are present:
* `dtc` - Execute the device tree compiler
* `-I dts` - The input file is in device tree source format
* `-O dtb` - The output file should be produced in device tree binary format
* `dt-blob.dts` - The first anonymous parameter is the input filename
* `-o dt-blob.bin` - The output filename

This should output nothing. If you get lots of warnings, you've forgotten the `-q` switch; you can ignore the warnings. If anything else is output, it will most likely be an error message indicating you have made a mistake in the device tree source. In this case, review your edits carefully (note that sections and properties *must* be semi-colon terminated for example), and try again.

Now the device tree binary blob has been produced, it needs to be placed on the first partition of the SD card. In the case of non-NOOBS Raspbian installs, this is generally the partition mounted as `/boot`:
```
$ sudo cp dt-blob.bin /boot/
```

However, in the case of NOOBS Raspbian installs, this is the recovery partition, which is not mounted by default:
```
$ sudo mkdir /mnt/recovery
$ sudo mount /dev/mmcblk0p1 /mnt/recovery
$ sudo cp dt-blob.bin /mnt/recovery
$ sudo umount /mnt/recovery
$ sudo rmdir /mnt/recovery
```

Please note that the filename and location are important. The binary blob must be named `dt-blob.bin` (all lowercase), and it must be placed in the root
directory of the first partition on the SD card. Once you have rebooted the Pi (to activate the new device tree configuration) you can test the flash with the following simple script:
```python
    import picamera

    with picamera.PiCamera() as camera:
        camera.flash_mode = 'on'
        camera.capture('foo.jpg')
```

You should see your flash LED blink twice during the execution of the script.

!!! warning
    The GPIOs only have a limited current drive which is insufficient for powering the sort of LEDs typically used as flashes in mobile phones. You will require a suitable drive circuit to power such devices, or risk damaging your Pi.

    For reference, the flash driver chips we have used on mobile phones will often drive up to 500mA into the LED. If you're aiming for that, then please think about your power supply too.

If you wish to experiment with the flash driver without attaching anything to the GPIO pins, you can also reconfigure the camera's own LED to act as the flash LED. Obviously this is no good for actual flash photography but it can demonstrate whether your configuration is good. In this case you need not add anything to the `pin_config` section (the camera's LED pin is already defined to use pull down termination), but you do need to set `CAMERA_0_LED` to absent, and `FLASH_0_ENABLE` to the old `CAMERA_0_LED` definition (this will be pin 5 in the case of `pins_rev1` and `pins_rev2``, and pin 32 in the case of everything else). For example, change:
```
    pin_define@CAMERA_0_LED {
        type = "internal";
        number = <5>;
    };
    pin_define@FLASH_0_ENABLE {
        type = "absent";
    };
```

into this:

```
    pin_define@CAMERA_0_LED {
        type = "absent";
    };
    pin_define@FLASH_0_ENABLE {
        type = "internal";
        number = <5>;
    };
```

After compiling and installing the device tree blob according to the instructions above, and rebooting the Pi, you should find the camera LED now
acts as a flash LED with the Python script above.