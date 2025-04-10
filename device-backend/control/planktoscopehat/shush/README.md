# ShushEngine

The Python stepper motor driver for Trinamic's TMC5160 motion controller chip.

This project is based on the @Roboteurs project [SlushEngine](https://github.com/Roboteurs/slushengine).  More details and their products can be found on their [website](https://roboteurs.com/).

Since this project uses Trinamic's famed *silent* stepper drivers and is based on the SlushEngine project, it's being called the ShushEngine.

This project is made for the Raspberry Pi only at this time.

## Getting Started

### Installing the ShushEngine project

In your Raspberry Pi, open a new Terminal window.

Change to the directory/folder in which you'd like to save your project.  For this example, let's just use the desktop.

```
cd Desktop
```

To get the ShushEngine project files onto your desktop, copy/paste or type the following.

```
git clone https://github.com/ZJAllen/ShushEngine.git
```

Now, change directory into the newly created `ShushEngine` folder.

```
cd ShushEngine
```

You're all ready to start using the ShushEngine!

### Simple Motor Control

The stepper motor driver chips used are [Trinamic TMC5160](https://www.trinamic.com/fileadmin/assets/Products/ICs_Documents/TMC5160A_Datasheet_Rev1.14.pdf), which use 256 microsteps per full step.  Most common stepper motors have 200 steps per revolution, or 1.8 degrees per step.  Therefore, if you want to go 1 full revolution, the TMC5160 would need a command to go 51,200 microsteps (256 * 200).  Keep this in mind for the following example.

The following example assumes the wiring according to Trinamic’s TMC5130-BOB Raspberry Pi [example](https://blog.trinamic.com/2019/03/29/internet-of-moving-things-tmc5130-raspberry-pi-3b/). This breakout board is similar to the TMC5160-BOB.

Below is a simple Python script to get the motor spinning.  You can run this by typing `python3 example.py` (once you're in the `/ShushEngine` root folder).  The example code is as follows:

``` python
import shush
import time

m = shush.Motor(0)
m.enable_motor()


# This function takes the target position as an input.
# It prints the current position and the iteration.
# The motor spins until it gets to the target position
# before allowing the next command.
def spin(target):
    m.go_to(target)

    i = 0

    while m.get_position() != target:
        print(m.get_position())
        print(i)
        i += 1


while(True):
    # Spin 5 rotations from start
    spin(256000)

    time.sleep(0.5)
    # Spin back 5 rotations to starting point
    spin(0)

    time.sleep(0.5)
```


## Motor Driver Functionality

This library is being populated with various functionality to drive stepper motors with ease.  Please check back to this list as the library is developed.

The following examples assume you have assigned the Motor object to the variable `m` as in `m = Shush.Motor(0)`, where the argument for Motor() is the identifier for the specific stepper motor.  If you have up to six stepper motors, for example, you can denote them by `m0 = Shush.Motor(0)`, `m1 = Shush.Motor(1)`, ..., `m5 = Shush.Motor(5)`.

---

### Go To Position

The `go_to()` method takes a target position as the input argument, and the driver internals drive the motor to that position according to the set ramp parameters.  The target position is number of microsteps.  The default is 256 microsteps per full stepper motor step.  Most common stepper motors move 1.8 degrees per step, or 200 steps per full revolution.  So to go a full rotation, the target would be +/- 51200 microsteps.

The position can be a signed (positive or negative) number.  The most negative number allowed is (-2^31), or -2,147,483,648, and the most positive number allowed is (2^31 - 1), or 2,147,483,647.

To put this range in perspective, if you set the position to the max or min value, it would spin +/- 41,943 **full rotations** from the 0 position.

#### Syntax:

``` python
m.go_to(512000)
```

#### Return:

None

---

### Get Current Position

The `get_position()` method retrieves the current position of the motor.  This method doesn't take any input arguments.

As described in the `go_to()` method, the position can be -(2^31) to +(2^31 - 1), so the position read from the register is also signed.

This method can be called during a motion to poll the position in real time.

#### Syntax:

``` python
current_position = m.get_position()
```

#### Return:

Signed position of motor [int]

---

### Spin at Set Velocity

The `move_velocity()` method runs the motor in either the positive or negative direction. The only required argument is the direction: 0 for positive, 1 for negative.

The optional arguemnts `v_max` and `a_max` are set by default, but can be changed if needed. If the velocity and/or acceleration is set in this method, it **is** retained, but not overwritten in the `Ramp()` class.  If you want to retrieve the previously set velocity and/or acceleration parameters, please see the `set_VMAX()` and `set_AMAX()` methods.

This method can be called during a motion either change direction, velocity, or change from position mode to velocity mode.

#### Syntax:

``` python
m.move_velocity(1)

m.move_velocity(0, v_max=51200, a_max=1000)
```

#### Return:

None

---

### Read Data in Register

The `read()` method gets data from a particular register in the driver.  It takes only the register address as the input argument, and it returns the value.

The returned value is, by default, an integer, but it can be parsed into binary or hex depending on your needs.

#### Synatax:

``` python
actual_position = m.read(Motor.Register.XACTUAL)
```

#### Return:

Data received from SPI read operation [int]

---

### Write Data to Register

The `write()` method sends data to a particular register in the driver.  It takes the register address and the data to be sent as the input arguments.  Since the register addresses in the datasheet are in hex, it is easy to send the address as hex.  The data can be sent as an int, as hex, or as binary.  The data representation for the *data* will vary for different registers.  Per the datasheet, for write access, 0x80 is added to the register address provided.  This is done internally by the method.

There is no return value for writes by default, so if you need a response from a particular register, please also use the `read()` method.

#### Synatax:

``` python
m.write(Motor.Register.XTARGET, 5000)
```

#### Return:

None

# License

The ShushEngine drives up to 6 stepper motors using Trinamic TMC5160 drivers.
Copyright (C) 2019 Zach Allen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
