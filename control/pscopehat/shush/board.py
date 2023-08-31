__author__ = "ZJAllen"

import shush.boards.pscope_hat_0_1 as s1

import spidev
import RPi.GPIO as gpio

gpio.setwarnings(False)


class Board:
    def __init__(self):
        # Initialize the peripherals (SPI and GPIO)
        self.init_spi()
        self.init_gpio_state()

    def init_gpio_state(self):
        # Sets the default states for the GPIO on the Shush modules.
        # Only applies to Raspberry Pi

        gpio.setmode(gpio.BCM)

        # Define chip select pins
        gpio.setup(s1.m0_cs, gpio.OUT)
        gpio.setup(s1.m1_cs, gpio.OUT)

        # Define error and stall pins
        gpio.setup(s1.error, gpio.IN)
        gpio.setup(s1.stall, gpio.IN)

        # Define enable pins
        gpio.setup(s1.m0_enable, gpio.OUT)
        gpio.setup(s1.m1_enable, gpio.OUT)

        # Pull all cs pins HIGH (LOW initializes data transmission)
        gpio.output(s1.m0_cs, gpio.HIGH)
        gpio.output(s1.m1_cs, gpio.HIGH)

    def init_spi(self):
        # Initialize SPI Bus for motor drivers.

        Board.spi0 = spidev.SpiDev()
        # Open(Bus, Device)
        Board.spi0.open(0, 0)
        # 1 MHZ
        Board.spi0.max_speed_hz = 1000000
        # 8 bits per word (32-bit word is broken into 4x 8-bit words)
        Board.spi0.bits_per_word = 8
        Board.spi0.loop = False
        # SPI Mode 3
        Board.spi0.mode = 3

        Board.spi1 = spidev.SpiDev()
        # Open(Bus, Device)
        Board.spi1.open(0, 1)
        # 1 MHZ
        Board.spi1.max_speed_hz = 1000000
        # 8 bits per word (32-bit word is broken into 4x 8-bit words)
        Board.spi1.bits_per_word = 8
        Board.spi1.loop = False
        # SPI Mode 3
        Board.spi1.mode = 3

    def deinitBoard(self):
        # Closes the board and releases the peripherals.
        gpio.cleanup()
