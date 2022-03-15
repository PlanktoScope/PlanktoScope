# Preliminary study of battery power

One of our goals is to be able to power the PlanktoScope on a portable battery to simplify the use in the field. We have therefore started to study the consumption of the PlanktoScope as well as the available hardware.

## Available hardware 03/2022

- 2 batteries of 15000 and 20000 mA/h. 
- 2 adapters usb 3.0 sector 5V-9V-12V.
- 3 power adapter 5V.
- 2 cables voltage converter 5V -> 12V.
- 1 adjustable power supply
  
## Point on the needs

- Raspberry Pi 4B: 5V and 3A
- Motor board assembly: 5-12VDC and 1.2A
  - Small Pump: 12V and 0.8A
  - Big Pump: 6-24V and 0.4-1.6A (10Wmax)

## Voltage check performed 

!!! Warning
    The small 5-12V voltage converter cable doesn't work with USB3.0, so you have to use the 2.0 5V adapters.

- Adapter + 5->12V converter cable long : 13.96V measured
- Adapter + Cable converter 5->12V short : 14.46V measured
- Power supply adjustable on 12V then 9V : 12.8V / 9.9V measured

## Current verification performed

To measure the current consumed when the motor board works, we created a circuit with a mutimeter in series at the output of the power supply. 
Then we ran the pump at its maximum power.

- Adapter + Cable converter 5->12V long : 346mA measured
- Adapter + Cable converter 5->12V short : 150mA measured
- Adjustable power supply on 12V : 1800mA measured
  
!!!Warning
    The value measured on the big power supply is very high and makes the voltage drop to 6V. In the futur we should understand why this happens to use it.


## First estimation of the battery life

Assuming the following power consumption using as power for the motors one of the cables and an adapter: 

- Raspberry Pi 4B specification: 500 - 900 maH
- Hat motor at full power: 350maH - 2000 maH (in the worst case we don't understand yet)
  
**Battery 1**: 

  - 15 KmaH -> x3.7V = 55Wh -> /5V = 11100 mAH available
  - Multiplied by 0.9 (taking 10% less for the loss) = 9990mAh available
  - Divided by (500+350mAH or 900+2000mAH) = 9,08h or 3.38h of autonomy

**Battery 2**:

  - 20 KmaH -> x3.7V = 74Wh -> /5V = 14800 mAH available
  - Multiplied by 0.9 (taking 10% less for the loss) = 13320mAh available
  - Divided by (500+350mAH or 900+2000mAH) = 12.1h or 4.51h of autonomy

!!!Warning 
    These estimates are a first calculation with the very approximate value that we have. The duration obtained seems to us very high by making turn the pump to its maximum of power. 
    But this is a start for further research on the consumption of the PlanktoScope.

## Problems when using the battery

The Raspberry Pi 4B does not turn on when using power via the battery even though the specifications match. We don't have an explanation for this yet.
