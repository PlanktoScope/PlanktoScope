# Changelog

## Image changelog

### V2.2.1: released 2021-05-11

Bugfix:

- Package update to fix an issue were newer boards would not get recognised properly, leading to an early crash of the python script.

Improvement:

- Addition of a small menu to switch branches of the software. This is going to be of use mainly to developers.

**[Image download link](https://drive.google.com/file/d/1y0k_NDXN0yT5caZrXhjLYXgQVxu-D5ql/view?usp=sharing)**

### V2.2: released 2021-01-15

Breaking changes:

- new UI: more intuitive and more complete, with data validations checks and helpful tooltips

Improvements:

- Random camera crash solved: instead of using the python picamera library, we now use a compiled binary, `raspimjpeg` (whose source code is [here](https://github.com/PlanktonPlanet/userland/tree/master/host_applications/linux/apps/raspicam)). It's controlled through a FIFO pipe.
- Raspberry HQ camera support (the pixels are bigger (1,55µm vs 1,12µm on the camera v2.1) so with the same optics, the resolving power of your images is going to be reduced at 1µm per pixel vs 0,7µm per pixel with the 25mm/16mm lens couple).
- White balance control of the image
- Data backup on USB drive: all the files contained in `/home/pi/data` are copied over to your usb key
- Integrity check of the generated files (for now only for raw pictures and `metadata.json`. A file called `integrity.check` is created alongside the images. This file contains one line per file, with the filename, its size and a checksum of both its filename and its content.
- Gallery: allows you to browse the data folder to see the images you captured and the segmentation results.
- Update mechanism: for now, this only updates the code of the PlanktoScope and not the underlying OS.
- Wifi configuration tab: you can configure the Wifi network you want the machine to connect to.
- Hardware configuration tab: to customize the settings dependind on the hardware you use, (pump steps per mL, stepper driver type).

Probably broken:

- Embedded segmentation: it's been a while since we touched it. It should still be working, but you may experience bugs with it... If that's the case, please come forward so we can help solve those before the next release!

**[Image download link](https://drive.google.com/file/d/1fht8r7P6_bVsfIIwo7wnGLQ_1uxWCnos/view?usp=sharing)**

### V2.1: released 2020-10-14

Breaking changes firsts:

- There is no GUI on this image, it was created based on the Raspberry OS Lite, so no GUI. A new non-lite version is expected for late next week.
- The wifi network is now named `PlanktoScope`, and the password to it is `copepode`.
- The default user is `pi` and the default password is `copepode` for this user.
- The images captured and the segmentation output is now in the folder `/home/pi/data`

Improvements:

- Under the hood, whole new code is running! There is still a small bug that is triggered when running long imaging sequences, if this happens, restart the machine! We are working on finding where the problem may comes from. This bug is chased here.
- Another change: automatic wifi setup! If you setup your Raspberry to connect to a wifi network (by configuring wpa_supplicant.conf) it will try to connect to this network before starting its hotspot. Also, if you connect it to a wired network via its Ethernet port, it will share this connection to devices connected to the hotspot!
- The documentation has been updated to include more information about the ribbon assembly and how to create a backup of your sd card!

**[Image download link](https://drive.google.com/file/d/1zOmbmXqt5uELQC0FTha1ndjJyMvehGSk/view?usp=sharing)**
