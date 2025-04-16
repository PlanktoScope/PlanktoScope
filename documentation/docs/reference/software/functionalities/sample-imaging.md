# Sample Imaging

This document explains how the PlanktoScope software captures images of samples and how it uses the image-acquisition settings exposed by the "Fluidic Acquisition" page of the PlanktoScope's Node-RED dashboard.

Currently, the PlanktoScope software only has one sample-imaging mode, which we call "stop-flow imaging":

## Stop-flow imaging

This imaging mode is optimized to allow capture of high-quality images using low-cost, high-resolution camera modules such as the [Raspberry Pi Camera Module 2](https://www.raspberrypi.com/products/camera-module-v2/) and the [Raspberry Pi High Quality Camera](https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/) (refer to the [hardware product specifications](../../hardware/product-specs.md) to see which camera modules are used in each version of the PlanktoScope hardware), whose [rolling-shutter](https://en.wikipedia.org/wiki/Rolling_shutter) designs can introduce artifacts around moving objects while the camera is capturing an image.

When this imaging mode is started, the PlanktoScope will repeatedly perform the following sequence of actions until a desired number of images ("Number of images to acquire" in the Node-RED dashboard) is captured:

1. The PlanktoScope's pump will pull some fixed volume of sample ("Pumped volume" in the Node-RED dashboard, in units of mL) from the sample intake and move the same volume of sample down through the PlanktoScope's flowcell.

2. After the PlanktoScope's pump finishes pumping the specified volume, the pump will stop and the PlanktoScope will wait for some short fixed duration of time ("Delay to stabilize image" in the Node-RED dashboard, in units of seconds). This waiting period is intended to allow the sample in the PlanktoScope's flowcell to stop flowing, so that all objects in the camera's field-of-view will (hopefully) stop moving - because moving objects will cause [distortion effects](https://en.wikipedia.org/wiki/Rolling_shutter#Distortion_effects) to appear in images captured with rolling-shutter cameras such as those used in the PlanktoScope.

3. The PlanktoScope will capture and save an image of its entire field-of-view.
