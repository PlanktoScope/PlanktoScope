#!/bin/sh -e

# Initialise GPIO 4 and 12 to output to release the steppers so that they can freely spin
# and they consume no power
if [ ! -e /sys/class/gpio/gpio4 ]; then
    echo "4" > /sys/class/gpio/export
fi

if [ ! -e /sys/class/gpio/gpio12 ]; then
    echo "12" > /sys/class/gpio/export
fi
echo "out" > /sys/class/gpio/gpio4/direction
echo "out" > /sys/class/gpio/gpio12/direction
echo "1" > /sys/class/gpio/gpio4/value
echo "1" > /sys/class/gpio/gpio12/value
