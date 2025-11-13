import adafruit_mcp4725  # type: ignore
import board  # type: ignore
import busio  # type: ignore

# Proportional 0 to VOLTAGE_MAX
DAC_MIN = 0
DAC_MAX = 4095

# at 3.3V the output range is 0-3300mV
# at 5V the output range is 0-5000mV
VOLTAGE_MIN = 0
VOLTAGE_MAX = 5000  # mV

i2c = None
dac = None


def map_to_voltage(value):
    return (value / DAC_MAX) * VOLTAGE_MAX


def map_to_value(voltage):
    return int((voltage / VOLTAGE_MAX) * DAC_MAX)


def on() -> None:
    assert dac is not None
    dac.raw_value = DAC_MAX


def off() -> None:
    assert dac is not None
    dac.raw_value = DAC_MIN


def save() -> None:
    assert dac is not None
    dac.save_to_eeprom()


def is_on() -> bool:
    return not is_off()


def is_off() -> bool:
    assert dac is not None
    return dac.raw_value == DAC_MIN


def init(address: int) -> None:
    global i2c, dac
    i2c = busio.I2C(board.SCL, board.SDA)
    dac = adafruit_mcp4725.MCP4725(i2c, address=address)
    dac.raw_value = 0


def deinit() -> None:
    if i2c is not None:
        i2c.deinit()


def get_state() -> tuple[float, int, int]:
    assert dac is not None
    return dac.normalized_value, dac.raw_value, map_to_voltage(dac.raw_value)


def set_value(value: float) -> None:
    assert dac is not None
    dac.normalized_value = value


def set_dac(value: int) -> None:
    assert dac is not None
    assert DAC_MIN <= value <= DAC_MAX
    dac.raw_value = value


def set_voltage(value: int) -> None:  # mV
    assert dac is not None
    assert VOLTAGE_MIN <= value <= VOLTAGE_MAX
    value = map_to_value(value)
    dac.raw_value = value
