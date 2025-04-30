# Changelog

The design of the PlanktoScope's hardware has been evolving to fix usability issues and improve the quality of images captured by the PlanktoScope. Thus, multiple versions of the hardware have been developed:

<!--

## v3.0

WORK IN PROGRESS

Replaces [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) with [Raspberry PI 5](https://www.raspberrypi.com/products/raspberry-pi-5/) for much faster CPU and GPU computing power.

Increased RAM from 4 to 8 GB.

Includes a [Real Time Clock (RTC)](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#real-time-clock-rtc) with [rechargeable battery](https://www.raspberrypi.com/products/rtc-battery/).

Includes [Raspberry Pi Active Cooler](https://www.raspberrypi.com/products/active-cooler/)

Features a [power button](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-button).

The PlanktoScope is now powered by the Raspberry via USB-C instead of by the hat.

Faster wifi from 120Mb/s to 300Mb/s

[PCIe connector](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-connector-for-pcie), compatible with:
* [Raspberry Pi AI HAT+](https://www.raspberrypi.com/products/ai-hat/)
* [Raspberry Pi SSD Kit](https://www.raspberrypi.com/products/ssd-kit/)

Easier access to the SD Card, no need for tweezers anymore

The Raspberry micro HDMI ports are now accessible

-->

## v2.6

This is the latest version of the PlanktoScope hardware, and it is the version currently sold by FairScope. It replaced the optical components so that the PlanktoScope produces higher-quality images.

## v2.5

This was the first version of the PlanktoScope hardware made commercially available by FairScope, a small business started by the inventor of the PlanktoScope in order to make it easier for people to obtain PlanktoScopes. It is a minor variation of the v2.4 hardware design and includes all of the changes made in previous hardware versions - including a custom-designed PCB HAT, a glass capillary flowcell. The mechanical structure of this design uses CNC-milled parts rather than laser-cut parts.

## v2.4

This was a prototype which replaced the ibidi u-Slide flowcell with a simpler flowcell design based on rectangular glass capillaries, in order to fix various issues with the ibidi flowcells and to make it possible for people to make their own flowcells.

This version was only an internal prototype for the PlanktoScope development team.

## v2.3

This was a prototype version of the hardware which replaced the Adafruit Stepper Motor HAT and the Yahboom RGB Cooling HAT with a custom-designed PCB HAT, in order to simplify overall assembly and provide additional features which solved problems with the v2.1 hardware design. As a result, a different configuration of the PlanktoScope software is required to control this version of the PlanktoScope hardware, as well as subsequent hardware versions. This version also significantly changed the physical dimensions of the PlanktoScope's mechanical structure, in order to solve some problems with the v2.1 design.

This version was only an internal prototype for the PlanktoScope development team.

## v2.2

This was a prototype version of the hardware which replaced the Adafruit Stepper Motor HAT with a Waveshare Stepper Motor HAT.

This version was only an internal prototype for the PlanktoScope development team.

## v2.1

This is the first version of the PlanktoScope hardware which was publicly released, and it is one of the two hardware designs described in the [initial paper](https://www.frontiersin.org/articles/10.3389/fmars.2022.949428/full) introducing the PlanktoScope. It simplified the hardware's robustness and mechanical assembly by integrating most subsystems into a monolithic architecture whose structure uses laser-cut parts. The electronic hardware components of this design are all available off-the-shelf, using an Adafruit Stepper Motor HAT to control various actuators and a Yahboom RGB Cooling HAT to cool the PlanktoScope's embedded Raspberry Pi computer. The mechanical structure was designed for fabrication using a laser cutter. This hardware version included some design flaws, such as providing no way to replace the Raspberry Pi's micro-SD card without partially disassembling the PlanktoScope.

## v1.0

This was the first prototype of the PlanktoScope, and it is one of the two hardware designs described in the [initial paper](https://www.frontiersin.org/articles/10.3389/fmars.2022.949428/full) introducing the PlanktoScope. Its mechanical structure featured a fully modular, stackable architecture consisting of triangular layers which coupled together with magnets.

This design was complicated to assemble, and it suffered from unreliable electronic communication between the modules, so it was never publicly released.
