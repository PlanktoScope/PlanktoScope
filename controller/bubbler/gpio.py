#!/usr/bin/env python3
import time
import board
import busio
import adafruit_mcp4725
import sys

def main():
    if len(sys.argv) != 6:
        print("Usage : python gpio.py start peak step delay target")
        sys.exit(1)

    # Lecture des arguments
    start = int(sys.argv[1])
    peak = int(sys.argv[2])
    step = int(sys.argv[3])
    delay = float(sys.argv[4])
    target = int(sys.argv[5])

    address = 0x60

    i2c = busio.I2C(board.SCL, board.SDA)
    dac = adafruit_mcp4725.MCP4725(i2c, address=address)

    print(f"🚀 MCP4725 @0x{address:02X}")
    print(f"Paramètres : start={start}, peak={peak}, step={step}, delay={delay}, target={target}")

    while True:

        # 1) Montée progressive start → peak
        print(f"↑ Montée progressive de {start} vers {peak}")
        for value in range(start, peak + 1, step):
            print(f"   DAC = {value}")
            dac.raw_value = value
            time.sleep(delay)

        # 2) Descente progressive peak → target
        print(f"↓ Descente progressive de {peak} vers {target}")
        for value in range(peak, target - 1, -step):
            print(f"   DAC = {value}")
            dac.raw_value = value
            time.sleep(delay)

        # 3) Mise à zéro
        print("→ DAC = 0 (1 s)")
        dac.raw_value = 0
        time.sleep(1)


if __name__ == "__main__":
    main()
