# PlanktoScope Hat Hardware

## Buses and GPIO pinout

### I2C1 Bus
#### RTC RV-3028-C7
Address 0x52
Configured through a kernel driver.

#### OLED Display
Address 0x3c

### SPI0 Bus
#### Motor Controller 0: TMC5160
Chip Enable: SPI0_CE0
Motor Enable: GPIO23

Diagnostic output:
GPIO16 for Error output
GPIO20 for Stall output


#### Motor Controller 1: TMC5160
Chip Enable: SPI0_CE1
Motor Enable: GPIO5

Diagnostic output:
GPIO16 for Error output
GPIO20 for Stall output

### GPIO
#### Fan control
PWM1 control through GPIO13

#### LED0 control
PWM0 control through GPIO18

#### LED1 control
PWM0 control through GPIO12


### I2C0 Bus
#### EEPROM M24C32
Address 0x50
For HAT information only.