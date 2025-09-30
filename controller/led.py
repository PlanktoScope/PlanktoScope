from smbus2 import SMBus
from time import sleep

MCP4725_ADDR = 0x60
bus = SMBus(1)


def set_voltage(vout):
    """
    Fixe la tension de sortie du MCP4725 (0–5.116 V mesurés)
    """
    code = int((vout / 5.116) * 65535)
    code = max(0, min(65535, code))  # sécurité
    high_byte = (code >> 8) & 0xFF
    low_byte = code & 0xFF
    bus.write_i2c_block_data(MCP4725_ADDR, 0x40, [high_byte, low_byte])


try:
    print("Rampe 0V → 5V")
    v = 0.0
    while v <= 5.0:
        print(f"Vout = {v:.1f} V")
        set_voltage(v)
        sleep(0.2)  # 200 ms
        v += 0.1

    print("Maintien à 5V pendant 2s")
    sleep(2)

    print("Retour à 0V")
    set_voltage(0.0)

except KeyboardInterrupt:
    set_voltage(0.0)

finally:
    bus.close()
