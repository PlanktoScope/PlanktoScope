#!/usr/bin/env python3
import sys
import board
import busio
import adafruit_mcp4725

def main():
    # Vérifie les arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage : python light.py <value> [i2c_address]")
        print("  <value> : entier entre 0 et 4095 (résolution 12 bits)")
        print("  [i2c_address] : optionnel, par défaut 0x62 (ex: 0x63)")
        sys.exit(1)

    # Lecture de la valeur
    try:
        value = int(sys.argv[1])
    except ValueError:
        print("Erreur : la valeur doit être un entier.")
        sys.exit(1)

    if not (0 <= value <= 4095):
        print("Erreur : la valeur doit être comprise entre 0 et 4095.")
        sys.exit(1)

    # Adresse I²C optionnelle
    address = 0x60  # adresse par défaut
    if len(sys.argv) == 3:
        try:
            address = int(sys.argv[2], 0)  # interprète automatiquement 0x..
        except ValueError:
            print("Erreur : l'adresse doit être un entier (ex: 0x62 ou 98).")
            sys.exit(1)

    # Initialisation du bus I²C et du DAC
    i2c = busio.I2C(board.SCL, board.SDA)
    dac = adafruit_mcp4725.MCP4725(i2c, address=address)

    # Application de la valeur
    dac.raw_value = value

    print(f"✅ MCP4725 @0x{address:02X} réglé à {value}/4095 ({value/4095*100:.1f}%)")

if __name__ == "__main__":
    main()
