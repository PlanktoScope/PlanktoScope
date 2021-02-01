# PlanktonScope Simple Setup Guide

## Download the image

For ease of setup, a preconfigured image is provided. You can download it from [here](https://drive.google.com/file/d/1fht8r7P6_bVsfIIwo7wnGLQ_1uxWCnos/view?usp=sharing).

## Writing the image to the SD card

Download the latest version of [balenaEtcher](https://www.balena.io/etcher/) and install it.

Connect an SD card reader with the micro SD card inside.

Open balenaEtcher and select from your hard drive the previously downloaded img file file you wish to write to the SD card.

Select the SD card you wish to write your image to.

Review your selections and click 'Flash!' to begin writing data to the SD card.

## Inserting the SD card
Once flashing is over, you can unmount the SD card from the computer (usually done by right clicking on the card icon in the taskbar).

Insert now the card in the Raspberry installed in your PlanktonScope.

## Install a mDNS client

To access the PlanktoScope services through your browser, you need to install a mDNS client.

If you are running a linux machine, you are in luck. Avahi-client is probably already installed on your machine. Check with your package manager.

If you are running a Windows machine, you will need to install the Bonjour service. It's a client developped by Apple. However, if you already use iTunes, Skype or even Photoshop, you may already have a client installed. Try skipping to the next step. If you can't access the linked page, come back here!

To install the client, download the installer [here](https://download.info.apple.com/Mac_OS_X/061-8098.20100603.gthyu/BonjourPSSetup.exe) and launch it.

## Start playing!

Start up your PlanktonScope and connect to its WiFi network. You can now access the webpage at http://planktonscope.local:1880/ui to start using your machine!