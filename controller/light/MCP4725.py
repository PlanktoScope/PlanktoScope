import board  # type: ignore
import busio  # type: ignore
import adafruit_mcp4725  # type: ignore

MCP4725_ADDR = 0x60
# Proportional 0 to 5V
VALUE_MIN = 0
VALUE_MAX = 65535
VOLTAGE_MIN = 0
# if you run it from 3.3V, the output range is 0-3.3V. If you run it from 5V the output range is 0-5V.
VOLTAGE_MAX = 5

i2c = busio.I2C(board.SCL, board.SDA)
dac = adafruit_mcp4725.MCP4725(i2c, address=MCP4725_ADDR)


def map_to_voltage(value):
    return (value / VALUE_MAX) * VOLTAGE_MAX


def map_to_adc(voltage):
    return int((voltage / VOLTAGE_MAX) * VALUE_MAX)


def on():
    dac.value = VALUE_MAX


def off():
    dac.value = VALUE_MIN


def save():
    dac.save_to_eeprom()


def is_on():
    return dac.value == VALUE_MIN


def is_off():
    return not is_on()


def init():
    dac.value = 0


def deinit():
    i2c.deinit()


def set_current(current):
    return
