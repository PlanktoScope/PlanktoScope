---
name: Test Suite Run
about: Run the test suite to help us
title: "Test Suite Run"
labels: test-run
assignees: ""
---

# Info

**PlanktoScope**

- Hardware version: eg `v2.5`
- Software version: eg `2025.0.0.alpha.1`
- Machine name: eg `sponge-care-245`
- Serial number: eg `U132` (leave empty if unknown)

**Computer**

- Operating system: eg `macOS 14.1`
- Browser: eg `Firefox 128`

**Comment**

Anything else worth knowing?

# Test suite

## Setup

1. [Set up the SD card and start the PlanktoScope](https://docs.planktoscope.community/setup/software/standard-install/)
2. [ ] The PlanktoScope asks for Hardware version

## Sample

1. Go to "Sample"
2. Select "Plankton net" for Sample gear
3. Fill the form
4. [ ] The calculations are correct

<!-- TODO: Add a tool to verify calculations -->

## Optic

**LED and preview**

1. [ ] "Light on" turns on the LED
2. [ ] The preview shows images without significant lag
3. [ ] Updating "ISO" modifies the image
4. [ ] Updating "Shutter Speed" modifies the image
<!-- 5. [ ] Verify white balance-->
5. [ ] "Light off" turns off the LED

**Focus**

1. [ ] "UP 1MM" moves the focus in one direction
2. [ ] "DOWN 1MM" moves the focus in the other direction
3. [ ] Quick succession of "UP 100MM" moves the focus in one direction
4. [ ] Quick succession of "DOWN 100MM" moves the focus in the other direction
5. [ ] "Focus Distance" and "Focus Speed" impacts "⩓" in one direction
6. [ ] "Focus Distance" and "Focus Speed" impacts "⩔" in the other direction
7. [ ] "STOP FOCUS" stops movement

<!-- TODO: Add focus scenarios -->

**Pump**

1. [ ] The left arrow pumps in one direction
2. [ ] The right arrow pumps in the other direction
3. [ ] "Flowrate" and "Volume to pass" impacts speed in one direction
4. [ ] "Flowrate" and "Volume to pass" impacts speed in the other direction
5. [ ] "STOP PUMP" stops the pump

<!-- TODO: Add pump scenarios -->

**Prepare**

Prepare tubing, sample and flowcell.

Setup focus in "Optic Configuration"

## Fluidic acquisition

**UI**

1. [ ] "Number of images to acquire" and "Pumped volume" correctly updates "Total imaged volume" and "Total pumped volume"
2. [ ] Delay to stabilize image cannot be lower than 0.1
3. [ ] Delay to stabilize image cannot be higher than 5
4. [ ] "Flowcell" offers 5 different options
5. [ ] "Statistics" is coherent with information entered in "Sample"

**Small capture**

1. Start acquisition with 5 images
2. [ ] "Capture progress" shows progress
3. Wait for completion
4. Go to "Gallery" in the menu
5. [ ] Go to `img` -> `<today's date>` -> `name of the sample` -> `name of the acquisition`
6. [ ] There are 5 jpeg images of acceptable quality
7. [ ] There is a `metadata.json` file with coherent information
8. [ ] There is an `integrity.check` file listing the 5 images and the `metadata.json` file
9. Open one of the image and click the "HD" button
10. The quality is acceptable and the focus is correct

**Big capture**

1. Start acquisition with 100 images

## Segmentation

1. Start segmentation
2. [ ] "Status" updates and shows progress
3. Wait for segmentation to complete
4. Note the number of object counts
5. Go to "Gallery" in the menu
6. [ ] Go to `objects` -> `<today's date>` -> `name of the sample` -> `name of the acquisition`
7. [ ] There are as many jpeg images as there were objects counted
8. [ ] The jpeg images are of acceptable quality9.
9. [ ] There is a `ecotaxa_<name of the acquisition>.tsv` file
10. Open one of the image and click the "HD" button
11. The quality is acceptable and the focus is correct

## Ecotaxa

1. Go to "Gallery" in the menu
2. [ ] Go to `export` -> `ecotaxa`
3. [ ] Download the `ecotaxa_<name of the acquisition>.zip` file
4. Go to Ecotaxa
5. Import the zip and wait for completion
6. [ ] The result on Ecotaxa matches expectations

## System Monitoring

1. "Metrics" are coherent
2. "Information" is correct

## Administration

1. [ ] Logs can be viewed and downloaded
2. [ ] "Restart Hardware Controller" button is working
3. [ ] "Restart Segmenter" button is working
4. [ ] "Reboot" button is working
5. [ ] "Shutdown" button is working

## Network

Replace `{machine-name}` with your PlanktoScope name.

### Direct Ethernet

1. Connect your computer to the PlanktoScope ethernet
2. PlanktoScope is accessible at
   1. [ ] [http://planktoscope.local](http://planktoscope.local)
   2. [ ] [http://pkscope.local](http://pkscope.local)
   3. [ ] [http://home.pkscope](http://home.pkscope)
   4. [ ] [http://192.168.5.1/](http://192.168.5.1/)
   5. [ ] [http://pkscope-{machine-name}.local/](http://pkscope-{machine-name}.local/)

### Direct WiFi

1. Connect your computer to the PlanktoScope WiFi hotspot
2. PlanktoScope is accessible at
   1. [ ] [http://planktoscope.local](http://planktoscope.local)
   2. [ ] [http://pkscope.local](http://pkscope.local)
   3. [ ] [http://home.pkscope](http://home.pkscope)
   4. [ ] [http://192.168.4.1/](http://192.168.4.1/)
   5. [ ] [http://pkscope-{machine-name}.local/](http://pkscope-{machine-name}.local/)

### LAN Ethernet

1. Connect the PlanktoScope to your router ethernet
2. PlanktoScope is accessible at
   1. [ ] [http://pkscope-{machine-name}.local](http://pkscope-{machine-name}.local)

<!--

### LAN WiFi

1. Connect the PlanktoScope to your router wifi
2. PlanktoScope is accessible at
   1. [ ] [http://pkscope-{machine-name}.local](http://pkscope-{machine-name}.local)

-->

## Additional tests

If you've run tests that are not included in this test suite, please describe them here and share results.
