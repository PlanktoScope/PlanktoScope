from gpiozero import LED
from time import sleep

# On utilise LED car c'est une sortie digitale simple
mos = LED(19)  # GPIO19

print("Test MOSFET ON/OFF sur GPIO19")

try:
    while True:
        print("ON")
        mos.on()  # active la sortie (MOSFET conducteur)
        sleep(2)

        print("OFF")
        mos.off()  # coupe la sortie (MOSFET bloqué)
        sleep(2)

except KeyboardInterrupt:
    print("Arrêt du test")
    mos.off()
