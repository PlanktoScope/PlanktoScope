import spidev
from gpiozero import DigitalOutputDevice, DigitalInputDevice

class Board:
    def __init__(self):
        # Initialize the peripherals (SPI and GPIO)
        self.init_spi()
        self.init_gpio_state()

    def deinitBoard(self):
        # Closes the board and releases the peripherals.
        self.deinit_gpio_state()
        self.deinit_spi()

    def init_gpio_state(self):
        # Sets the default states for the GPIO on the Shush modules.
        # Only applies to Raspberry Pi

        # Define error and stall pins
        self.error = DigitalInputDevice(16)
        self.stall = DigitalInputDevice(20)

    def deinit_gpio_state(self):
        self.error.close()
        self.stall.close()

    def init_spi(self):
        # Initialize SPI Bus for motor drivers.

        # SPI for motor 0
        spi0 = spidev.SpiDev()
        # Open(Bus, Device)
        spi0.open(0, 0)
        # 1 MHZ
        spi0.max_speed_hz = 1000000
        # 8 bits per word (32-bit word is broken into 4x 8-bit words)
        spi0.bits_per_word = 8
        spi0.loop = False
        # SPI Mode 3
        spi0.mode = 3
        Board.spi0 = spi0

        # SPI for motor 1
        spi1 = spidev.SpiDev()
        # Open(Bus, Device)
        spi1.open(0, 1)
        # 1 MHZ
        spi1.max_speed_hz = 1000000
        # 8 bits per word (32-bit word is broken into 4x 8-bit words)
        spi1.bits_per_word = 8
        spi1.loop = False
        # SPI Mode 3
        spi1.mode = 3
        Board.spi1 = spi1

    def deinit_spi(self):
        self.spi0.close()
        self.spi1.close()
