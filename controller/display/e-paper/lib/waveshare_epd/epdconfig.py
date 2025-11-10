import os
import sys
import time
import logging

logger = logging.getLogger(__name__)

class RaspberryPi:
    # Pin definition
    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 4    # Custom Chip Enable GPIO4
    BUSY_PIN = 24
    PWR_PIN  = 18
    MOSI_PIN = 10
    SCLK_PIN = 11

    def __init__(self):
        import spidev
        import gpiozero
        
        self.SPI = spidev.SpiDev()
        self.GPIO_RST_PIN  = gpiozero.LED(self.RST_PIN)
        self.GPIO_DC_PIN   = gpiozero.LED(self.DC_PIN)
        self.GPIO_CS_PIN   = gpiozero.LED(self.CS_PIN)
        self.GPIO_PWR_PIN  = gpiozero.LED(self.PWR_PIN)
        self.GPIO_BUSY_PIN = gpiozero.Button(self.BUSY_PIN, pull_up=False)

    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            if value:
                self.GPIO_RST_PIN.on()
            else:
                self.GPIO_RST_PIN.off()
        elif pin == self.DC_PIN:
            if value:
                self.GPIO_DC_PIN.on()
            else:
                self.GPIO_DC_PIN.off()
        elif pin == self.CS_PIN:
            if value:
                self.GPIO_CS_PIN.on()
            else:
                self.GPIO_CS_PIN.off()
        elif pin == self.PWR_PIN:
            if value:
                self.GPIO_PWR_PIN.on()
            else:
                self.GPIO_PWR_PIN.off()

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        elif pin == self.RST_PIN:
            return self.GPIO_RST_PIN.value
        elif pin == self.DC_PIN:
            return self.GPIO_DC_PIN.value
        elif pin == self.CS_PIN:
            return self.GPIO_CS_PIN.value
        elif pin == self.PWR_PIN:
            return self.GPIO_PWR_PIN.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        self.GPIO_PWR_PIN.on()
        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self):
        logger.debug("spi end")
        self.SPI.close()

        self.GPIO_RST_PIN.off()
        self.GPIO_DC_PIN.off()
        self.GPIO_CS_PIN.off()
        self.GPIO_PWR_PIN.off()
        logger.debug("close 5V, Module enters 0 power consumption ...")

        self.GPIO_RST_PIN.close()
        self.GPIO_DC_PIN.close()
        self.GPIO_CS_PIN.close()
        self.GPIO_PWR_PIN.close()
        self.GPIO_BUSY_PIN.close()

# Création de l’instance unique pour Raspberry Pi
implementation = RaspberryPi()

# Export des fonctions globalement dans le module epdconfig
for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))
