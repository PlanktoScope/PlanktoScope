# Assembly guide of the PlanktoScope

![Complete](assembly_guide/pictures/1.webp)

## Step 0: Laser cutting

First, you need to make all the laser cuts to have all the necessary plexiglass parts, these cuts are made in opaque and transparent plexiglass of 5 mm, 2 mm and 3 mm. You can download the different plans in .svg format by clicking here. Make sure all holes are complete, and negative space is clear.

Gather all these pieces on a flat surface and make sure you have all the pieces you need to build the PlanktoScope

![Plans](assembly_guide/pictures/2.webp)

You can download them through the following links :

- [Opaque 5mm](https://espaces-collaboratifs.grenet.fr/share/proxy/alfresco-noauth/api/internal/shared/node/bZeqlLdjQDyYsn-WNXW_sw/content/opaque_5mm.svg?c=force&noCache=1647254539000&a=true)
- [Part B2 3mm](https://espaces-collaboratifs.grenet.fr/share/proxy/alfresco-noauth/api/internal/shared/node/ZA5Bbd68QBqe6xo_dzGR2Q/content/P1_2mm.svg?c=force&noCache=1647254588338&a=true)
- [Part B1 2mm](https://espaces-collaboratifs.grenet.fr/share/proxy/alfresco-noauth/api/internal/shared/node/Jw0G6g8oQQSvTEc5jW3r0A/content/P1_3mm.svg?c=force&noCache=1647254628010&a=true)
- [Transparent 5mm](https://espaces-collaboratifs.grenet.fr/share/proxy/alfresco-noauth/api/internal/shared/node/5PYgHMnoRoezJFbSeDCGZA/content/transparent_5mm.svg?c=force&noCache=1647254661127&a=true)

!!! Warning
    If you are doing the laser cutting yourself, please take the time to check the calibration of the machine and its power output for the material you are using. A tight fit is needed between the different plates to avoid unwanted play between critical parts.

!!! Warning
    Depending on the reference of your pump the plans may not be adapted despite the efforts made to have universal plans.

## Step 1: Gather everything you need

Next, gather all the components needed to build your PlanktoScope by referring to the following list:

- M12 lenses
- Peristaltic pump and tubing
- Raspberry Pi, motor driver board, GPIO connectors
- Flashed SD card
- Stepper motors
- PiCam and flex cable
- GPIO ribbon connector, headers, HATs, LED
- DC Power terminal
- Magnets
- Super glue
- Standoffs (M2.5), M3 screws and nuts

Make sure you have your screwdriver kit, soldering iron, and components ready. Also, remember to flash the PlanktoScope image disk on the SD card before installing the Raspberry Pi.

If you are not familiar with any process, such as soldering, tapping, or wiring, try and familiarize yourself with the topics first.

Soldering deals with high heat and potentially toxic materials, so make sure to use the proper precautions.

## Step 2: Lenses tapping and mounting

Before starting the assembly and mounting of the different components we will first prepare and mount some parts such as first prepare and mount some parts such as lenses.

You now need to tap the holes for the M12 lenses in stage and mount it the different K pieces. We must also tap the part D located just after the camera. It is helpful for alignment to do  both the objeDtive and tube lens mount together. It is important to do this as straight as  possible. A drop of mineral or olive oil can help the process. Be careful to use a right-hand tap  (that goes down when turning clockwise).

![Step2](assembly_guide/pictures/3.webp)

You should get the following set of parts with lenses knowing that this can change depending on the number of lenses you have for the part K.

![Step2](assembly_guide/pictures/4.webp)
![Step2](assembly_guide/pictures/5.webp)

## Step 3: Magnets setup

Now is a good time to think about how the magnets will function within the microscope. The magnets in the sample stage will need to attract to the magnets on the flow cell holder. The magnets in the objective holder will need to attract the magnets on the mount. Keep this in mind as you are adding your magnets and tapping your respective M12 holders so your orientation will be correct.

To summarize the set of magnets to be placed, there are magnets between:

- Part D and part A2,
- Part G and part A2,
- The part D and the part J2,
- Part G and part J2,
- The part E and the parts containing the different lenses K
 
The magnets in parts D, G, A2 and J2 must be placed in such a way that the plates fit together as shown in the picture below.

![Step3](assembly_guide/pictures/6.webp)

The magnets in parts E and K must be placed in such a way that the plates fit together as shown in the picture below.

![Step3](assembly_guide/pictures/7.webp)

The same operation can be repeated on the different plates K containing the lenses.


You can now fix your magnets into their appropriate holes. It is recommended to glue the magnets in place. If the magnets are too large to fit in, the holes can be widened with a handheld drill. However, they should be quite snug in place. Before you glue them in place make sure that the polarity is maintained, as they will be impossible to remove after gluing.

## Step 4: Standoff installation

![Step4](assembly_guide/pictures/8.webp)

Place 8 standoffs (M2.5 6mm) into the designated holes on the laser-cut base A1. A pair of
pliers make the job more comfortable. Do not overtighten as it is possible to crack the base
material.

![Step4](assembly_guide/pictures/9.webp)

## Step 5: Sample stage assembly

You can now fit the pegs on the driver mounts into the corresponding holes on the sample
stage. They should be glued in place with superglue or epoxy. You can spin the shaft to align
the driver mounts on the 2 steppers if it helps making the process easier.

![Step4](assembly_guide/pictures/10.webp)
![Step4](assembly_guide/pictures/11.webp)

You should now have a sample stage and motor assembly that looks like this.

## Step 5: Camera preparation

You can now unscrew the lens from the Pi camera, being careful not to disturb the sensor below.

![Step5](assembly_guide/pictures/12.webp)

## Step 6: Camera mount

You can mount the camera using the appropriate holes on the camera mount **C**. Be careful to avoid getting oil or dust on the sensor.

![Step6](assembly_guide/pictures/13.webp)

## Step 7: LED preparation

![Step7](assembly_guide/pictures/14.webp)

The LED can then be wired up and put into its mount **H**. If you wire the LED yourself, remember to give enough length to reach the motor driver on the other end of the microscope. You can also add a bit of glue to fix **H** to the motor mount **G** at this time to make assembly easier, though it is not required.

!!! warning
    ![Step7](assembly_guide/pictures/15.webp)

    This picture shows the correct wiring for the LED. Please make sure the red wire is on the long pin of the LED.


## Step 10: Vertical slices assembly

You can now start placing the motor mount/LED assembly,

1. We start by adding the part **E**,

![Step10](assembly_guide/pictures/16.webp)

2. Then we add the parts **C** and **D**,

![Step10](assembly_guide/pictures/17.webp)

3. Then the part **G**,

![Step10](assembly_guide/pictures/18.webp)

4. And finally the **H** part.

![Step10](assembly_guide/pictures/19.webp)

## Step 11: Pump setup

The pump can then be mounted in place on **I1** and **I2**. Thread the wires through the hole with the pump tubing pointed toward the holes on the mount. Then fix the pump in place.

![Step11](assembly_guide/pictures/20.webp)

## Step 12: Connectors

Now we'll move on to fixing the various connectors of our Planktoscope, i.e. the power supply and the GPS, which are connected to the outside of the PlanktoScope. To do this, we take parts **B1** and **B2** and the connectors below.

![Step12](assembly_guide/pictures/21.webp)

For the power supply we have soldered the + and - as above. We now fix them on the part **B2** by passing them through then by tightening them by paying attention to the direction of the plate so that they are directed towards outside. The result is as follows.

![Step12](assembly_guide/pictures/22.webp)

You can if you want glue the **B1** and **B2** together keeping them well aligned but it is not mandatory.

## Step 13: Motor HAT wiring

First, insert and solder the terminal blocks and headers onto the motor driver PCB.

![Step13](assembly_guide/pictures/23.webp)

Now that all the components to be connected to the motor board and the board itself are ready, we will carry out all the wiring. To do this we will follow the diagram below.

![Step13](assembly_guide/pictures/24.webp)

!!! info
    The PlanktoScope **uses only bipolar stepper motors** (with 4 wires coming out, and two coils inside), so you need to identify the two wires working together for each coil. The [RepRap Wiki has great information](https://reprap.org/wiki/Stepper_wiring#.22pair.22_wires_on_4_wire_motors) on how to do this, either with a multimeter or without.
    
    You can find more information about stepper motors and how they work in this [document](http://resources.linengineering.com/acton/attachment/3791/f-00ca/1/-/-/-/-/Stepper%20Motor%20Basics.pdf).

!!! tip
    If your wires are too short, you can invert the pump and the focus wiring. However, you will have to remember to change the configuration later on.

!!! tip
    Make sure the wires are properly connected by pulling on them a little. They should not come loose.
    
Once done it should look like the image below.

![Step13](assembly_guide/pictures/25.webp)

To facilitate the organization of the cables in your PlanktoScope, don't hesitate to use tape or other material to hold them together and prevent them from being disordered

After all the wiring is done, you can attach the board to the **A1** part as shown in the image below.

![Step13](assembly_guide/pictures/26.webp)

To fix it we will place directly 6mm standoffs with a nut.

## Step 14: Assemblage
We can now place the different parts that we have made (LED/motor/camera, pump, connectors) on the three parts **A1**, **A2** and **A3** taking care to fit the different parts together. For the moment we don't fix the parts **A1**, **A2** and **A3** to the rest we will do that at the end. Our PlanktoScope is starting to take shape. 

Now that everything is in place you can place the different cables in the holes provided on parts **C**, **D**, **E**, **F** and **G** as below.

![Step14](assembly_guide/pictures/27.webp)

## Step 15: Raspberry Pi setup and installation

![Step15](assembly_guide/pictures/28.webp)

At this point, you can insert your flashed SD card into your Raspberry Pi. [Consult the guide for flashing your SD card](https://www.planktoscope.org/replicate/assemble-your-kit) before you do this. The heat sink can also be added to the processor.

!!! note
    If you choose the Expert path, you still need to flash your sd card, either with the [lite version](https://downloads.raspberrypi.org/raspios_lite_armhf_latest) of Raspberry OS or with the [desktop version](https://downloads.raspberrypi.org/raspios_armhf_latest).

Mount the Raspberry Pi containing the flashed SD card on the standoffs attached to the lasercut base **A1**. You will obtain this:

![Step15](assembly_guide/pictures/29.webp)

Don't hesitate to hide the excess cables of the different motors/pumps behind the Raspberry Pi so that it doesn't interfere with the rest. We fix the Raspberry Pi this time using 10mm standoffs.

## Step 16: Prepare the GPS HAT

Insert the battery to power the GPS HAT and solder the terminal mounts in place.

![Step16](assembly_guide/pictures/30.webp)
![Step16](assembly_guide/pictures/31.webp)

## Step 17: Install the GPS HAT

Mount the GPS HAT over the motor driver PCB using the standoffs attached to the laser cut base **A1**.

![Step17](assembly_guide/pictures/32.webp)

We obtain the following result:

![Step17](assembly_guide/pictures/33.webp)

## Step 18: Camera flex cable

At this point you can use the Pi camera flex cable to connect the camera to the Pi. This is done
by gently pulling up the tensioners, inserting the cable in the right orientation, then pushing
the tensioners back in place to set the cable. Try not to kink or fold the flex cable too much as
it is possible to damage it.

![Step18](assembly_guide/pictures/33.1.webp)

## Step 19: Install the Fan HAT

![Step19](assembly_guide/pictures/34.webp)

Place the cooling fan HAT above the Raspberry Pi by mounting it to the standoffs on base **A1**.

!!! warning
    Be careful to slide the camera flat cable in the slot in the HAT above the connector.
    
We obtain the following result:

![Step19](assembly_guide/pictures/35.webp)

## Step 21: Secure the HATS

![Step21](assembly_guide/pictures/36.webp)

Secure the cooling fan HAT and GPS HAT by tightening the 8 screws to the standoffs on base **A1**.

## Step 22: Insert the camera ribbon cable in the camera

![Step22](assembly_guide/pictures/37.webp)

You can now connect the camera flex cable into the connector on the camera board. Once again, gently pull up the tensioners, insert the cable in the right orientation, and push the tensioners back in place to set the cable. Try not to kink or fold the flex cable too much as it is possible to damage it.

## Step 23: Assemble the GPIO ribbon cable

If you didn't get an already assembled ribbon cable, you need to build it yourself.

The orientation of the connector does not really matter. However, you need to make sure that both connectors are oriented in the same direction and are on the same side of the ribbon.

To assemble, slide the ribbon in its connector and close it off. You need to tighten it really hard. It's very warmly recommended to use a vice to do so.

!!! warning
    Once assembled, the ribbon should NOT look like this:

    ![Step23](assembly_guide/pictures/38.webp)

    It should rather look like this:

    ![Step23](assembly_guide/pictures/39.webp)

## Step 24: Insert the ribbon cable

![Step24](assembly_guide/pictures/40.1.webp)

Attach the GPIO ribbon to connect the cooling fan HAT to the GPS HAT.

!!! tip
    You can try to route the flat ribbon from the camera under the ribbon cable you are connecting now.
    ![Step31](assembly_guide/pictures/40.webp)

## Step 25: Install side panel
![Step25](assembly_guide/pictures/41.webp)

Place the side plate **J** into the designated slots on the base.

## Step 26: Install the other side panel
![Step26](assembly_guide/pictures/42.webp)

Mount the side plate **K** on base **A** using the assigned slots.

## Step 27: Secure the sides together
![Step27](assembly_guide/pictures/43.webp)

Secure the laser cut sides with the screws and nuts.

## Step 28: Secure the sides to the base plate
![Step28](assembly_guide/pictures/44.webp)

Secure the laser cut sides to the base plate **A** with the screws and nuts.

!!! warning
    To make this easier, you can turn the assembly upside down or on its side. Be careful when doing so as the plates may fall.

## Step 29: Fluidic assembly

Assemble the different pipes so that it looks like the picture below.

![Step28](assembly_guide/pictures/44.1.webp)

## Step 30: Close your PlanktoScope

!!! warning
    Take a moment to check your wiring one last time. Also check the routing, make sure the LED wires and the pump stepper wires are in their dedicated channel.

Place the top **L** into the slots on the PlanktoScope body. Secure it in place with screws and nuts.
![Step30](assembly_guide/pictures/45.webp)


## Step 31: Enjoy!

Congratulations on a job well done. You can have some rest, get a tea and some biscuits!

![Step31](assembly_guide/pictures/1.webp)

You can now plug the machine in and test it. If you have choose the Expert's path, now is a good time to [finish setting up your machine](expert_setup.md).

## Step 32: Read the getting started guide
[A guide to get started with your machine use is available!](getting_started.md)
