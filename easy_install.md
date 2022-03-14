# PlanktoScope Simple Setup Guide

## Download the image

For ease of setup you have 2 choice.

   * Install classic version of PlanktoScope folow this link [PlanktoScope-v2.3](https://s3.bazile.io/planktoscope/images/planktoscope-v2.3-adafruit-final.img.gz) 
  
   * Install custom version base on PlanktoScope-v2.3 but specif to the project Lackoscope, please download the image : [PlanktoScope-v2.3-IESE_2022](https://s3.bazile.io/planktoscope/images/planktoscope-v2.3-adafruit-final.img.gz) 


## Prepare your SD card

1. To start choose an SD card without data (All data will be remove during flash)
2. Connect SD card to your computer
3. Download and install a software to flash OS images onto SD cards. For example you can use [BalenaEtcher](https://www.balena.io/etcher/)

Now we can flash SD card with the sofware that you choose. For this follow the step :

1. Open your soft (for the rest of this demonstration we can use BalenaEtcher).

![Balena](getting_started/balena1.webp)

2. In the first step select `flash from file` and choose the image (previously downloaded).

![Balena](getting_started/balena2.webp)

3. Select your device to click on `Select target` and choose the good SD card.

![Balena](getting_started/balena3.webp)

!!! warning
    Please take care to choose the right card. For this you can check the name and/or the size.

4. To clik on `Flash!` and wait few minute (take a break ☕+🥐)

![Balena](getting_started/balena4.webp)

!!! Tip
    You need to unmount your device before removing.


## Install into the PlanktoScope

Currently you have an SD card with a software for the PlanktoScope. Now insert SD card into the PlanktoScope and connect it to the electrical grid.

When the light bellow fan hat is blue this mean that the installation went smoothly and that the Planktoscope is ready ✅.

!!! Tips 
    If you want more information about sens of led colors please read this section: [here](debug.md#others-informations)

## Pump value setup

If you use one of us Planktoscope (project Lacoscope number 0,1,2 or 3) you can directly select your machine version. This step allows you not to have to calibrate the pump.

Here are the steps to follow :

1. On Node-red interface (http://planktoscope.local:1880/ui) go to the page `Hardware Settings`
2. In the section `Machine version` select your PlanktoScope (project Lacoscope number)


Else you need to calibrate your PlanktoScope please got to calibration section : [Calibration](calibration.md#pump-calibration)


## Start Playing !!!

Now you can start to play with your new Planktoscope. For that we need to connect your computer to PlanktoScope Wifi's.

- Wifi Ssid start by `PlanktoScope-Baba*****-******`  
(example PlanktoScope-Babajai_Muqouqo)

- Wifi Password is `copepode`

!!! Tip
    The name of ssid is display on the screen above fan hat

When you are connect to PlanktoScope Wifi, you just need to follow this link [http://planktoscope.local:1880/ui](http://planktoscope.local:1880/ui)  to access the control panel.

If you have not yet assembled your PlanktoScope, go to the [Assembly Guide](assembly_guide.md).

## Install a mDNS client

To access the PlanktoScope services through your browser, you need to install a mDNS client.

If you are running a linux machine, you are in luck. Avahi-client is probably already installed on your machine. Check with your package manager.

If you are running a Windows machine, you will need to install the Bonjour service. It's a client developped by Apple. However, if you already use iTunes, Skype or even Photoshop, you may already have a client installed. Try skipping to the next step. If you can't access the linked page, come back here!

To install the client, download the installer [here](https://download.info.apple.com/Mac_OS_X/061-8098.20100603.gthyu/BonjourPSSetup.exe) and launch it.
