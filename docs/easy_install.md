
# PlanktoScope Simple Setup Guide

## Download the Image

To make setup easier, a preconfigured image is provided for download. You can download the image from [this server](https://drive.google.com/file/d/199HycSWPt5980B0qhXNyW6VexvZhHLs4/view?usp=share_link).

## Write the Image to the SD Card

1. Download and install the latest version of [balenaEtcher](https://www.balena.io/etcher/).
2. Connect an SD card reader with the micro SD card inside.
3. Open balenaEtcher and select the img file you downloaded earlier.
4. Select the SD card you want to write the image to.
5. Review your selections and click 'Flash!' to begin writing data to the SD card.

## Insert the SD Card

Once the flashing process is complete, unmount the SD card from your computer (usually done by right-clicking on the card icon in the taskbar). Insert the card into the Raspberry Pi installed in your PlanktoScope.

## Install an mDNS Client

To access the PlanktoScope services through your browser, you will need to install an mDNS client.

- If you are running a Linux machine, you may already have the Avahi client installed. Check with your package manager.
- If you are running a Windows machine, you will need to install the Bonjour service. If you already have iTunes, Skype, or Photoshop installed, you may already have a client installed. If you can't access the linked page, come back here to install the client. To install the client, download the installer [here](https://download.info.apple.com/Mac_OS_X/061-8098.20100603.gthyu/BonjourPSSetup.exe) and launch it.

## Start Using the PlanktoScope

1. Start up your PlanktoScope and connect to its WiFi network. 
2. Access the web page at http://planktoscope.local:1880/ui to start using your machine. If you are having DNS issues, use this URL instead: http://192.168.4.1:1880/ui/.
