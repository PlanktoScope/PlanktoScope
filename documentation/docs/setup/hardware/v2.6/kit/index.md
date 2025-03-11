# Kit Production
## Kit Composition
In this section you will go through all the steps to supply and create your PlanktoScope kit.
You can find a list of the components needed in the [Planktoscope V2.6 BOM](../../../../assets/hardware/v2.6/Planktoscope_V2.6_BOM.xlsx).

| Files                                                                                | Description                       |
|--------------------------------------------------------------------------------------|-----------------------------------|
| [Planktoscope V2.6 BOM](../../../../assets/hardware/v2.6/Planktoscope_V2.6_BOM.xlsx) | Bill Of Material for PlanktoScope |

We tried to have the most easy-to-supply components, you still may have to adapt and research for new suppliers according to product availability and your location.
If you find some local alternative please share your custom BOM to our GitHub Discussions thread for [v2.6 Localized Hardware BOMs](https://github.com/PlanktoScope/PlanktoScope/discussions/502), so that other members of our community can learn from your work!

In the following sections we will go more in detail on:

- The possibility to machined on your own the [Mechanical Structure](#mechanical-structure)
- The documentations and assembly steps to manufacture the [PlanktoScope HAT V1.3](#planktoscope-hat-13-pcb)
- The cabling steps of the [LED Assembly](#led-assembly), the [Alim Jack Assembly](#alim-jack-assembly) and the [OnOff Button Assembly](#onoff-button-assembly)
- Finaly the [Optic 20-200 Assy](#optic-20-200-assembly) & the [Fluidic Line Set Up](#fluidic_line_set_up)


## Mechanical Structure

In order to create the PlanktoScope case, parts were designed to be machined with a CNC milling machine. 
The configuration of the CNC milling machine plays a crucial role in the machining process and can significantly affect the quality and efficiency of the production of a workpiece. You will have to adapt the file to your machine as every CNC milling machine gets its characteristics: feed rate and diameter adjustment according to your machine and selected end mill. 
And don't forget safety, use your nicest protective glasses! :-)

![Bamboo Structure V2.6 dxf view](images/Bamboo_Structure_V2.6_dxf_view.png "Bamboo Structure V2.6 dxf view")


### Manufacturing file

Here you can find the Fusion link to the Planktoscope V2.6 Case file. You will be able to download on every format you prefer.
It is mostly the .dxf which is interesting to create the program on a CNC milling machine. The file .step will also help you to understand the depth of the various pocket and perform modification if you need.
If you do not have the equipment and/or the knowledge do not hesitate to contact local suppliers and fablabs. 


!!! note

	Depending on stock availability, FairScope can also be considered as a supplier for the Structure Bamboo Plate.
    

| Files                                            | Description                            |
|--------------------------------------------------|----------------------------------------|
| [PlanktoScope_CaseV2.6](https://a360.co/40VXXBz) | PlanktoScope V2.6 Case for CNC Milling |


This .dxf file has been designed for a **thickness of the material at 7.6mm (3 inches)**. 

For a different thickness you’ll need to adapt it.

!!! tips

	For a better assembly and if your software does not add it automaticaly use "dog bone" filet on every corner. :bone:

![Dogbone example.png](images/Dogbone_example.png)

### Material
A great variety of material can be used to create the PlanktoScope case. You need to be sure that it can be machined easily and has great durability in harsh conditions. Here you can find 2 examples of used material: Bamboo Plywood & Valchromat.

1. Bamboo Plywood

Bamboo plywood is a renewable, eco-friendly material made from layers of bamboo strips pressed together. It is known for its strength, durability, and resistance to warping, making it ideal for furniture. Bamboo plywood is lightweight, versatile, and more sustainable than traditional hardwoods, as bamboo grows quickly and requires fewer resources to cultivate.
FairScope is using Bamboo Plywood for V2.6.

2. Valchromat

Valchromat is a wood-based composite material made from recycled wood fibers and colored with natural dyes. It is known for its durability, resistance to moisture and decay, and ability to be machined and finished in a similar way to solid wood.


### Finnish of the plates

After your successful milling process, remove all dust and remains of the milling and machining.

Here you can use your favorite finishing according to the selected material. Be sure that it remains as environmentally friendly as possible.

!!! note

	For example, FairScope uses Rubio Monocoat Plus. It is a wood finishing product that is designed to provide a durable, natural-looking finish to wood surfaces. It is made from plant-based oils and pigments, which give it a transparent finish that enhances the natural aspect of the wood.

Dry all parts and store them for the assembly process.

![Bamboo Structure V2.6 exploded view](images/Bamboo_Structure_V2.6_exploded_view.png "Bamboo Structure V2.6 dxf view")
## PlanktoScope Hat 1.3 PCB

Welcome to the PCB production manual for the PlanktoScope Hat 1.3!

![Hat_recto_verso](images/Hat_recto_verso.PNG "Hat_recto_verso")

A **Printed Circuit Board (PCB)** is a vital component of electronic devices, providing physical support and electrical connections for components. The PCB production process involves three main stages:

1. Design: Engineers use software (e.g., Altium, KiCad) to create the schematic and layout, optimizing component placement, trace paths, and layers.

2. Fabrication: Copper and fiberglass sheets are processed via etching, plating, drilling, and layer stacking to form the circuit structure.

3. Assembly: Components are placed and soldered either manually or with automated systems.

Components assembled on PCBs are either **Thru-Hole** (leads pass through the board, ideal for durability) or **Surface Mount** (soldered directly on the surface, suited for compact designs). The choice depends on the device’s requirements.

You will find in the following files the full documentation to start a quotation on your favorite electronic prototypist platefrom.
We will also guide you through the assembly of side components (Dirvers & Fan) to complete the PlanktoScope HAT 1.3 fabrication.

!!!note

	Depending on stock availability, FairScope can also be considered as a supplier for the fully assembled PlanktoScope HAT 1.3.

### PCB Manufacturing Information

#### PCB Manufacturing Files

| Files                                                                                                                 | Description                                                                                                                   |
|-----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| [Gerber files PlanktoScope HAT V1.3.zip](../../../../assets/hardware/v2.6/Gerber_files_PlanktoScope_HAT_V1.3.zip)     | The exported Gerber files for PCB fabrication                                                                                 |
| [Assembly files PlanktoScope HAT V1.3.zip](../../../../assets/hardware/v2.6/Assembly_files_PlanktoScope_HAT_V1.3.zip) | The SMD components list and assembly footprints, Pick-and-place machine instructions, Additional data for ThruHole components |

Some components are missing from the "Pick-and-Place machine instructions" file. Please refer to the document titled "PlanktoscopeHat-v1.3-fab\_thru-hole component (missing from PnP).jpg" for further details.

We recommend asking your prototypist to assemble all the thru-hole components. In order to reduce costs and if you feel like doing it, you can assemble them manually, you will have to adapt the BOM and be really cautious of the correct solderings.

The assembly of the Drivers TMC 5160 and the Axial Fan assembly are here proposed in parallel and DIY. No worries, everything is explain in [Assembly of the Drivers TMC 5160](#assembly-of-the-drivers-tmc-5160) & [Assembly of the Axial Fan](#assembly-of-the-axial-fan). 
They are not included in Thru-Hole components list for the prototypiste.

#### Configuration on prototypist website

When you ask an electronic proptypist to create your PCB and assemble the components, technical informations will be asked. The following configuration parameters can be used to this purpose.

!!! note

	Please note that the naming may vary depending on the manufacturing company you use and are only intended to provide you with support. You can, of course, adjust the parameters as you see fit.

##### Board dimensions

65 mm x 100 mm

##### Circuit specifications

| Property                               | Value      |
| -------------------------------------- | ---------- |
| Material                               | FR4        |
| Thickness                              | 1.6 mm     |
| Finish                                 | Chem. gold |
| Number of layers                       | 2          |
| Specific stackup                       | sans       |
| SMD sides                              | top        |
| Finished external copper thickness (µ) | 35 µm      |
| Internal copper thickness (µ)          | without    |
| IPC Class                              | Class 2    |

##### Solder mask

| Property      | Value     |
| ------------- | --------- |
| Solder mask   | TOP + BOT |
| Mask colour   | green     |
| Peelable mask | without   |

##### Marking

| Property         | Value     |
| ---------------- | --------- |
| Silkscreen (ink) | TOP + BOT |
| Ink colour       | white     |
| ROHS marking     | without   |
| UL marking       | without   |
| Date marking     | without   |

##### Specific options

| Property                   | Value     |
| -------------------------- | --------- |
| Space between tracks       | > 0.15 mm |
| Min. drill hole size       | > 0.20 mm |
| Blind via                  | with out  |
| Cross blind                | no        |
| Burried via                | na        |
| Impedance control          | no        |
| Edge plating               | no        |
| Press-fit                  | no        |
| Carbon                     | without   |
| Via Fill                   | without   |
| Beveled edge               | without   |
| Contersunk holes           | without   |
| Contersunk holes (qty/PCB) | without   |
| Metallographic section     | without   |
| Gold fingers (thickness)   | without   |
| Gold fingers (qty/PCB)     | without   |

You should receive a PCB looking similar to the following pictures (top & bottom):
![Hat_recto_verso_2](images/Hat_recto_verso_2.PNG "Hat_recto_verso_2")

#### Next steps
As explain earlier on and in order to let you dive into a fun DIY project, some soldering is about to come! In the following steps, we’ll guide you through assembling the Drivers TMC 5160 (used to control the peristaltic pump and the linear stepper motors) and the Axial Fan. Let’s get started!

### Assembly of the Drivers TMC 5160

These steps will show you how to correctly solder driver boards on their connectors. 

#### Tooling :hammer_and_wrench:

- [ ] Soldering Iron
- [ ] Solder
- [ ] Breadboard
- [ ] Utility Knife / Razor Blade
- [ ] Multimeter

![Drivers_toolings](images/Drivers_toolings.JPG "Drivers_toolings")

When you solder this for the first time, take special care to gather information and train yourself. Do not hesitate to have a look to this [Soldering 101: Beginners Guide](https://www.youtube.com/watch?v=rK38rpUy568).

#### Assembly Steps

**1. Prepare the components**

| Component                            | Example of reference | Qty |
|--------------------------------------|----------------------|-----|
| Driver TMC 5160 SilentStepStick      | 700-TMC5160SILENTSTE | 2   |
| Connector Header Vertical 2POS .54MM | 732-5315-ND          | 1   |

![Drivers_components](images/Drivers_components.JPG "Drivers_components")

!!! note

	Usually 2 Connectors Header of 8 position comme alongside each Driver. If it is not the case you can also buy one with many position and cut it in order to gets 4x8 pins and 2x2 pins connectors.

Unpack the Drivers TMC 5160, the Connector Header strips of 8 pins (x2) and 2 pins(x1), take the breadboard and warm your soldering iron.

**2. Cut the via bridge**

:hammer_and_wrench:
[Tooling](#tooling): 

- [ ] Utility Knife / Razor Blade
- [ ] Multimeter

Bridge Cut: use a **razor blade or a utility knife** to unable conductivity between 2 of the 4 slots as shown in the following visual:

![Drivers_bridge_cut](images/Drivers_bridge_cut.PNG "Drivers_bridge_cut")

Check if the two slots are correctly isolated from one another with a **multimeter** in conductivity mode.

![Drivers_bridge_cut_check](images/Drivers_bridge_cut_check.JPG "Drivers_bridge_cut_check")

!!! warning

	This step does not really follow traditional methods, be careful to only cut this bridge and keep the PCB integrity.

**3.  Set in position the Connector Header strips**

Plug the connectors with the appropriate distance to the **breadboard**.

![Drivers_positioning](images/Drivers_positioning.JPG "Drivers_positioning")

The breadboard supports you during soldering to ensure the spacing and angle of the Connectors.


**4.  Set in position the Drivers TMC 5160 PCB**

Positioned the Drivers TMC 5160 PCB on the connectors set on the breadboard.

!!! warning

	Make sure that the larger chip labeled "trimatik" is positioned on the bottom of the board and the four smaller chips are positioned on the top of the board as shown in the picture.

**5.  Soldering**

Now solder all pins of the connectors strip.

![Drivers_soldering](images/Drivers_soldering.JPG "Drivers_soldering")

!!! tips

	You can solder one pin on one side and then the opposite pin on the other side to secure your workpiece, ensuring it stays in place without shifting accidentally while you solder the other pins.


#### Finalisation & Installation

Re do the operation for the second Driver TMC 5160. 

Install it on your PlanktoScope Hat 1.3 on the designated connectors. In order to avoid any electric continuity between the 2 Drivers, you can spray them with some tropicalization varnish or add electronic tape between both.

### Assembly of the Axial Fan

These steps will show you how to install the axial fan on the PlanktoScope Hat 1.3 and how to create soldering bridges at the bottom of the board.

#### Tooling :hammer_and_wrench:

- [ ] Professional Soldering Iron
- [ ] Solder
- [ ] Classic Pliers
- [ ] Screwdriver Hex 2
- [ ] Wires Stripper pliers

![Axial_fan_toolings](images/Axial_fan_toolings.JPG "Axial_fan_toolings")

#### Assembly Steps

**1. Prepare the components**

| Component                             | Example of reference | Qty |
|---------------------------------------|----------------------|-----|
| PlanktoScope HAT 1.3 PCB              |                      | 1   |
| Axial Fan RS PRO 5 V - 40 x 40 x 10mm | 789-7858             | 1   |
| Screw TBHC EMBASE M3X14 INOX A2       | TBHCEMB03/014A2      | 4   |
| Square nuts M3x5.5x1.8                | ECRCAR03/05/05A2     | 4   |

![Axial_fan_components](images/Axial_fan_components.JPG "Axial_fan_components")

**2. Install the Axial Fan**

:hammer_and_wrench:
[Tooling](#tooling): 

- [ ] Wire stripper pliers
- [ ] Screwdriver Hex2
- [ ] Classic Pliers

Cut off the wires of the Axial Fan in order to leave about 6 cm.
Strip the wires on 5mm with **Wire stripper pliers**.

![Axial_fan_preparation](images/Axial_fan_preparation.JPG "Axial_fan_preparation")

Install the fan on the top side of the PlanktoScope HAT 1.3 PCB. 

Pay attention to the **running direction** with the arrow marking on the side of the Axial Fan. The Axial Fan should **blow on the Raspberry Pi** (from Top to Bottom of the PlanktoScope HAT 1.3 PCB).
Engage the wire through the hole in the PlanktoScope HAT 1.3 PCB to reach the bottom side of the board.

![Axial_fan_placement](images/Axial_fan_placement.JPG "Axial_fan_placement")

Screw the 4x **M3*14 Screw** with **Screwdriver Hex2** and **Classical pliers**.
![Axial_fan_fixing](images/Axial_fan_fixing.JPG "Axial_fan_fixing")

**3. Solder the wires**

Tin the wires extremities. Solder the fan cables according to the marking and color codes:

- Black ⚫ on GND
- Red 🔴 on VCC

![Axial_fan_tining](images/Axial_fan_tining.JPG "Axial_fan_tining")

![Axial_fan_wire_soldering](images/Axial_fan_wire_soldering.JPG "Axial_fan_wire_soldering")

**4. Solder bridges**

Create soldering bridges between:

- The 2 slots of J3
![Axial_fan_J3_bridge](images/Axial_fan_J3_bridge.JPG "Axial_fan_J3_bridge")

- The middle slot and +5V. _(leaving +12V slot isolated)_
![Axial_fan_5V_bridge](images/Axial_fan_5V_bridge.JPG "Axial_fan_5V_bridge")
    
- The middle slot and )D. _(leaving IC slot isolated)_
![Axial_fan_D_bridge](images/Axial_fan_D_bridge.JPG "Axial_fan_D_bridge")
  
Final result:

![Axial_fan_bridge_final](images/Axial_fan_bridge_final.JPG "Axial_fan_bridge_final")

Congratulation! You have finished to assemble the PlanktoScope HAT 1.3 PCB components, it should look like on the following picture:

photo hat terminé

## Cabling Component
The next step of the kit preparation is to prepare some cabling: by using standard component with few simple cabling steps it become possible to get tailor maid component for the PlanktoScope.

In the following chapters we will go through soldering and crimping adventures.

For this the needed equipments will be:
#### Tooling :hammer_and_wrench:

- [ ] Professional Soldering Iron
- [ ] Solder
- [ ] Crimping pliers
- [ ] Stripping pliers
- [ ] Third Hand / small Anvil
- [ ] Heat Gun
      
![Cabling_toolings](images/Cabling_toolings.JPG "Cabling_toolings")

You willl also need, in addition to the component themselves, some consumable:
#### Consumable:

- [ ] Heat Shrink Black
- [ ] Heat Shrink Red
- [ ] Wire Crimps
- [ ] Zip Ties

!!! note

	You can find reference example in the "Consumable" section of the Planktoscope V2.6 BOM.

### LED Assembly

A simple first assembly is the LED Assembly.

**1. Prepare the components**

| Designation                       | Qty | Example of reference  |
|-----------------------------------|-----|-----------------------|
| JST 1.25mm Male Connectors 200 mm | 1   | Ali Express - JST-200 |
| Super Bright White 5mm LED        | 1   | Mouser - 485-754      |

Here the JST connector proposed is already wired.

![Led_Assy_components](images/Led_Assy_components.JPG "Led_Assy_components")

**2. Prepare the wires**

With the **stripping pliers** stripped the wire over 5mm.

**3. Set Heat Shrink**

Slide a **Black heat shrink** on both of the wires. Slide an aditional and smaller **Red Heat Shrink** on the red wire.

![Led_Assy_heat_shrink](images/Led_Assy_heat_shrink.JPG "Led_Assy_heat_shrink")


**4. LED configuration**

Find the cathode (smaller) and anode (longer) pin of the **LED**.

![Led_Assy_polarity](images/Led_Assy_polarity.JPG "Led_Assy_polarity")

**5. Wires soldering on Led pin**

Maintain the LED or the wires with the **third hand**. Add some soldering material to both the wires extremities and to the pins of the LED.
Solder:

- the red wire🔴 to the anode (longer pin)
- the black wire⚫ to the cathode (small pin).

![Led_Assy_wires_solder](images/Led_Assy_wires_solder.JPG "Led_Assy_wires_solder")


**6. Heat Shrink heating**

Slide the heat shrink on the soldering and use the **heat gun** to secure it. 

- First the red one which make sure <ins>no contact can be made between the 2 pins</ins>.
- Second the black one to insulate from outside environnement

![Led_Assy_heat_shrink2](images/Led_Assy_heat_shrink2.JPG "Led_Assy_heat_shrink2")

**7. Led Assembly is ready!**
   
![Led_Assy_final](images/Led_Assy_final.JPG "Led_Assy_final")

### Alim Jack Assembly

The Alim Jack Assembly will be the link between the external 12V adaptor to the internal electronic system.

**1. Prepare the components**
   
| Designation                          | Qty | Example of reference                        |
|--------------------------------------|-----|---------------------------------------------|
| DC Power Jack Shield - 5,5mm 2,1mm   | 1   | Amazon CC 5,5*2,1mm DC DC power Jack Female |
| Bullet Connector 3.5mm Male + Female | 1   | Amazon B081TXM3XN                           |

![Alim_Jack_Components](images/Alim_Jack_Components.JPG "Alim_Jack_Components")

**2. Heat Shrink set up**

Set 15mm of Black and Red Heat Shrink respectively on the Black and Red wires.

![Alim_jack_heat_shrink](images/Alim_jack_heat_shrink.JPG "Alim_jack_heat_shrink")

**3. Soldering for red wire**

Maintain the **Female Bullet Connector** up on the **Small Anvil**, warm it with the **Solder Iron tip**, fill the chambre of the connector with some soldering material and dive the 🔴**Red Wire** in. Remove the solder iron. Wait the soldering material to dry.

**4. Heat Shrink heating**

Slide the  Red Heat Shrink on the female connector. <ins>Be careful of covering all the metalic part.</ins> Use the **heat gun** to secure it.

![Alim_jack_red_wire](images/Alim_jack_red_wire.JPG "Alim_jack_red_wire")

**5. Soldering for black wire**

Same operations with the **Male Bullet Connector** and the ⚫**Black Wire**.

<ins>Be careful of covering just the begining of the metalic connector.</ins>

!!! warning

	It will be plugged to the OnOff Button Assembly so each connector male or female must be solder carefully to be pluggable. It is made in opposition to be sure that black wire will go with white wire and red wire with the yellow one.

**6. Alim Jack Assembly is ready!**

   ![Alim_Jack_final](images/Alim_Jack_final.JPG "Alim_Jack_final")

### OnOff Button Assembly

The OnOff Button Assembly will be place between the Alim Jack Assembly and the PlanktoScope Hat 1.3. It will play the role of the switch On & Off of the PlanktoScope.

**1. Prepare the components:**

| Designation                                    | Qty | Reference           |
|------------------------------------------------|-----|---------------------|
| Electrically locked push buttons Gebildet 16mm | 1   | Amazon - E222       |
| Bullet Connector 3.5mm Male + Female           | 1   | Amazon - B081TXM3XN |

![OnOff_button_component](images/OnOff_button_component.JPG "OnOff_button_component")

**2. Preparation of the Push Button Gebildet**

Remove ⚪**White Wire** by firmly pulling on it. Prepare each wire end (white wire included) with a 1 cm striping.

   ![OnOff_button_prépa](images/OnOff_button_prépa.JPG "OnOff_button_prépa")

**3. Wire crimp Red & Green**

Use the **Crimping Plier** to add a wire crimp on the **🔴Red + :green_circle: Green wires**.

**4. Heat Shrink heating**

Slide the Red Heat Shrink on the female connector. Use the **heat gun** to secure it.

![OnOff_button_crimp_rg](images/OnOff_button_crimp_rg.JPG "OnOff_button_crimp_rg")

**5. Wire crimp Black & White**

Use the **Crimping Plier** to add a wire crimp on the **⚫ Black + ⚪ White wires**.

**6. Heat Shrink heating**

Slide the Black Heat Shrink on the female connector. Use the **heat gun** to secure it.

![OnOff_button_crimp_bw](images/OnOff_button_crimp_bw.JPG "OnOff_button_crimp_bw")

**7. Soldering for White wire**

Maintain the **Female Bullet Connector** up on the **Small Anvil**, warm it with the **Solder Iron tip** and fill the chambre of the connector with some soldering material and dive the other extemity of the ⚪**White wire** in. Remove the solder iron. Wait the soldering material to dry.

**8. Heat Shrink heating**

Slide the Black Heat Shrink on the female connector. <ins>Be careful of covering all the metalic part.</ins> Use the **heat gun** to secure it.

  ![OnOff_button_solder_f](images/OnOff_button_solder_f.JPG "OnOff_button_solder_f")

**9. Soldering yellow wire**

Same operation with the **Male Bullet Connector** and the :yellow_circle: **Yellow Wire**.
<ins>Be careful of covering just the begining of the metalic connector with heat shrink.</ins>

   ![OnOff_button_solder_m](images/OnOff_button_solder_m.JPG "OnOff_button_solder_m")

!!! warning
	
    It will be plugged to the Alim Jack Assembly so each connector male or female must be solder carefully to be pluggable. It is made in opposition with Alim Jack Assembly to be sure that white wire will go with black wire and the yellow wire with the red wire.

**10. Finalize**

Use 4 **Zip Ties** to secure the wires together.

![OnOff_button_final](images/OnOff_button_final.JPG "OnOff_button_final")

OnOff Button is ready!

## Optic Assembly

One of the crucial part of the PlanktoScope is the Optic. It is **THE most sensitive assembly** as the sensor of the PI Camera HQ will be unprotected for few minutes.
**To perform this assembly, make sure your workstation is as clean as possible: dust will be our worst ennemy during this step**.

![Optic_Assy_scheme](images/Optic_Assy_scheme.JPG "Optic_Assy_scheme")

Prepare the following toolings:
#### Tooling :hammer_and_wrench:

- [ ] Screwdriver Hex 1.5
- [ ] Specific Thorlab tooling SPW909
- [ ] A caliper

![Optic_Assy_tools](images/Optic_Assy_tools.JPG "Optic_Assy_tools")
### Optic 20-200 Assembly

**1. Prepare the components:**

| Designation                                     | Qty | Reference example |
|-------------------------------------------------|-----|-------------------|
| HQ Camera Pi Official - C to CS                 | 1   |                   |
| CM1L10 - Extension Tube, Internal SM1 Threading | 1   | Thorlabs CM1L10   |
| S1TM12 - SM1 to M12 x 0.5 Lens Cell Adapter     | 2   | Thorlabs S1TM12   |
| M12 Lens 25MM 5MP 1/2"                          | 1   | Jetsun M12-25-5MP |
| M12 Lens 12MM 5MP 1/2.5"                        | 1   | Jetsun M12-12-5MP |


![Optic_Assy_components](images/Optic_Assy_components.JPG "Optic_Assy_components")

**2. Lens on lens Adapter**

Set the  **M12/25 Lens** and the **M12/12 Lens** on each of the **S1TM12 Lens Adapters**.

![Optic_Assy_lens1](images/Optic_Assy_lens1.JPG "Optic_Assy_lens1")

**3. Remove the retaining ring**

Remove the retaining ring in the **CM1L10 Extension Tube**

**4. M12/25 Lens Insertion**

Insert the M12/25 Lens in the CM1L10 Extension Tube. Threaded side of the lens first. By using the **Tooling SPW909** set the lens Adapter at **14.7mm** deep.

![Optic_Assy_lens1_25](images/Optic_Assy_lens1_25.JPG "Optic_Assy_lens1_25")

Control the deepness of the Lens adaptor with a caliper. The distance must be measured between the surface of the lens adaptor and the last surface of the extension tube. Adjust the assembly to 
acheive 14,7mm (+/-0,05mm).


![Optic_Assy_scheme2](images/Optic_Assy_scheme2.JPG "Optic_Assy_scheme2")

**6. Protective cap removal**

Remove M12/25 & M12/12 Lens protective caps on lens side.

![Optic_Assy_caps](images/Optic_Assy_caps.JPG "Optic_Assy_caps")

**7. M12/25 Lens Insertion**

Insert the M12/12 Lens in the CM1L10 Extension Tube.Threaded side of the lens out. By using the Tooling SPW909 screw gently up to contact with the M12/25 Lens. _If you go gently no worries of damaging anything, the contact zone will not be between the 2 lens directly but between the 2 black casing diameter._
   Set back the protective cap.
![Optic_Assy_lens1_12](images/Optic_Assy_lens1_12.JPG "Optic_Assy_lens1_12")

**8. Disengage cable ribbon**

Open gently the connector and disengage the cable ribbon. Save it for later on assembly.

![Optic_Assy_cable_ribbon](images/Optic_Assy_cable_ribbon.JPG "Optic_Assy_cable_ribbon")

**9. Remove black holding extension**

Remove the black holding part of the **HQ Camera Pi**  with the  **Screwdriver Hex 1.5**. We will not use it afterwards.

![Optic_Assy_holding](images/Optic_Assy_holding.JPG "Optic_Assy_holding")

**10. Remove IR Filtre**

Follow the [official tutorial from RaspBerry to remove the IR Filtre](https://www.raspberrypi.com/documentation/accessories/camera.html#filter-removal).

!!! note

	 Do not hesitate to warm a bit the UV Filter with a heat gun or a hair dryer to soften the glue.

!!! warning

	This step is critical, try to remove the IR filtre without breaking it. If it is broken, clean as much as possible to remove all glass debris. Anyway, set your camera sensor asside and in a protected area during this operation. All dust and glass debris on the sensor will be really visible and emphasized during use afterward.

**11. Optical canon on Rpi HQ Camera**

Remove M12/25 2nd protective cap. Do a small air cleaning with a dust blower. You can now assemble the Optical canon assembly with the HQ Camera Pi. 
     
![Optic_Assy_assembly](images/Optic_Assy_assembly.JPG "Optic_Assy_assembly")

!!! note

	On the first PlanktoScope switch on, you will see the results of this assembly. If some dust is visible use really carefuly a small dust blower to remove it from the camera sensor.

**12. The Optic 20-200 Assembly is ready!**

![Optic_Assy_final](images/Optic_Assy_final.JPG "Optic_Assy_final")


## Fluidic Line Set Up

The next, and final step, of this kit preparation is to create the tubing needed for the fluidic line to carry the sample from the syringue to the "trash tube".

Prepare the following toolings:
#### Tooling :hammer_and_wrench:

- [ ] Utility knife
- [ ] Measuring ruler
- [ ] Drill
- [ ] 5mm drill bit
- [ ] 1mm drill bit

### Trash Falcon tube assembly

**1. Prepare the components:**

| Designation                                                                                | Qty   | Reference example   |
|--------------------------------------------------------------------------------------------|-------|---------------------|
| Falcon tube conic 50ml                                                                     | 1     | B088RCY7TG          |
| Barbed to Female Luer Adapter for 1/16"                                                    | 1     | CIL-P-857           |
| 2.4mm elbow connector                                                                      | 1     | AliExpress - EC-2.4 |
| Flexible Tube Saint Gobain Tygon® E-3603 PVC Special, Ø 1.6mm x Ø 3.2mm, L 15m Transparent | 10 cm | ACF00002            |

**2. Tap preparation**

Drill at the **center** of the Falcon Tube tap a hole with the **5mm drill bit**.
Drill at **5-10mm from the center** of the Falcon Tube tape a hole with the **1mm drill bit**.
Insert the **2.4mm elbow connector** in the 5mm holle. Secure it with the nut.

**3. Tubing set up**

Cut a **10cm lenght** of **Flexible Tube Saint Gobain Tygon® Ø 1.6mm**
On one end of the tube plug the elbow connector. Warming lightly the tube can help you for the insertion.
On the other end plug the **Barbed to Female Luer Adapter for 1/16"**.

### Tubing for the fluidic line

**1. Prepare the components:**

| Designation                                                                                | Qty    | Reference example |
|--------------------------------------------------------------------------------------------|--------|-------------------|
| Barbed to Male Luer Adapter for 1/16"                                                      | 1      | CIL-P-850         |
| Barbed to Female Luer Adapter for 1/16"                                                    | 1      | CIL-P-857         |
| Flexible Tube Saint Gobain Tygon® E-3603 PVC Special, Ø 1.6mm x Ø 3.2mm, L 15m Transparent | 3*10cm | ACF00002          |
| Robert clip for soft tubing 3 to 6 mm                                                      | 1      | RCST3.6           |


**2. Cut the tube**

Cut 3 times **10cm lenght** of **Flexible Tube Saint Gobain Tygon® Ø 1.6mm**.

**3. Assemble the connector and tubing**

* 1x10cm Tubing with 1 Male Luer Adapter
* 1x10cm Tubing with 1 Female Adapter
* 1x10cm Tubing with 2 Male Luer Adapter and the Robert clip in between

**The Fluidic Line is ready!**

## To be continued...

Congratulation, if you make it to the end of this "Kit Section" you have successfully to supplied and manufactured the entire BOM of the PlanktoScope V2.6.

We would be thrilled to have you continue your journey with us as we move on to the next phase of the documentation in the [assembly](../assembly/index.md) section. :flying_saucer: :microbe:
