# Changelog

## Image changelog

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