# PlanktoScope Hardware

This section of the PlanktoScope documentation will help you to build the hardware of a PlanktoScope. Our documentation splits this PlanktoScope production process into two phases: making a kit of parts, and assembling a PlanktoScope from that kit of parts.

If you do not already have a kit of parts, you will need to either purchase a kit or make a kit yourself. You will need to choose a PlanktoScope hardware version and obtain the hardware components necessary for that hardware version; your assembly kit will consist of those components. You can purchase a kit from [FairScope](https://www.fairscope.com), a small business started by the inventor of the PlanktoScope in order to make it easier for people to obtain PlanktoScopes. Once you have selected a hardware version, you can proceed to our instructions for making your kit.

If you do already have a kit of parts, you can proceed to our instructions for assembling your kit into a PlanktoScope. However, you will first need to determine the PlanktoScope hardware version which your kit is made for, so that you can choose the correct assembly guide for your kit.

## Hardware versions

The design of the PlanktoScope's hardware has been evolving to fix usability issues and improve the quality of images captured by the PlanktoScope. Thus, multiple versions of the hardware have been developed. This page only describes hardware versions for which documentation has been published  for anyone to manufacture the hardware, and here we only describe aspects of each hardware version relevant to choosing a version to manufacture. Due to a lack of time by the people developing the PlanktoScope hardware, documentation for other versions of the PlanktoScope hardware has not yet been created; for information on these other versions of the PlanktoScope hardware, please refer to the [technical reference](../../reference/hardware/changelog.md) section of our documentation site.

### Hardware v2.1

This was the first publicly released version of the PlanktoScope hardware. The electronic components of this design are all available from commercial off-the-shelf sources, using an Adafruit Stepper Motor HAT to control various actuators and a Yahboom RGB Cooling HAT to cool the PlanktoScope's embedded Raspberry Pi 4 computer. The mechanical structure was designed for fabrication using a laser cutter. This hardware version has some design flaws, such as providing no way to replace the Raspberry Pi's micro-SD card without partially disassembling the PlanktoScope; these problems have been fixed in later versions of the PlanktoScope hardware.

This version of the PlanktoScope hardware is the only version which has been widely replicated by independent makers so far. Currently, its manufacturing documentation is provided by [an older documentation site](https://planktoscope.readthedocs.io) which is no longer maintained, and it has not yet been migrated into our current documentation site. Additionally, this hardware design uses a peristaltic pump which is no longer commercially available, so anyone making an assembly kit for this version will have to identify a different pump to use as a substitute.

### Hardware v2.5

This version includes many design improvements to solve various problems with the v2.1 hardware design, including:

- Replacing the ibidi flowcell with a simpler glass capillary flowcell.

- Replacing the Adafruit Stepper Motor HAT with a HAT designed specifically for the PlanktoScope (the [PlanktoScope HAT](../../reference/hardware/hat.md)).

- Replacing the linear actuators for sample focusing with a more mechanically robust pair of linear actuators.

- Replacing the peristaltic pump with a more accurate pump which is commercially available.

- Making the Raspberry Pi's micro-SD card accessible without requiring disassembly of the PlanktoScope.

The mechanical structure of this design uses CNC-milled parts rather than laser-cut parts.

Our documentation site provides manufacturing documentation to make assembly kits for this hardware version, and to assemble kits for this version into PlanktoScopes.

### Choosing a version

We recommend building a PlanktoScope of the latest available hardware version (currently v2.5). However, if you are making your own assembly kit and the following limitations apply to you, you may need to choose an older hardware version such as v2.1:

- You do not have access to a CNC mill, or to a commercial fabrication service with a CNC mill.

- You do not have access to manufacturing capabilities for assembling a custom printed circuit board, and you cannot buy a pre-assembled HAT from FairScope.

## Building a PlanktoScope

If you received a PlanktoScope hardware assembly kit from someone but you are not sure what hardware version the kit is for, you should check with the person who gave the kit to you.

Once you have figured out what hardware version of the PlanktoScope you will build, you can proceed to our version-specific hardware setup guides:

- If you are building a PlanktoScope with the v2.5 hardware, please proceed to our page for [Hardware v2.5](./v2.5/index.md) to find instructions for making an assembly kit, as well as instructions for building a PlanktoScope from an assembly kit for v2.5 of the hardware.

- If you are building a PlanktoScope with the v2.1 hardware, please proceed to our page for [Hardware v2.1](./v2.1/index.md) to find instructions for making an assembly kit, as well as instructions for building a PlanktoScope from an assembly kit for v2.1 of the hardware.

## Next steps

After making an assembly kit (if necessary) and building a PlanktoScope from your assembly kit, you should proceed to our [software setup guide](../software/index.md).
