# Very inspired by https://github.com/bgawalt/uuidBabyName
import re, uuid, random, os

consonants = "bcdfgjklmnpqrstvwxy"
vowels = ["a", "e", "i", "o", "u", "ai", "eo", "ou", "io", "au", "ao", "ui", "oa"]

combos = []
for con in consonants:
    for vow in vowels:
        combos.append(con + vow)
combos += ["puo", "loi", "boi", "roi", "toi", "foi", "poi", "tuo", "ruo"]


def popHexPair(s):
    if len(s) < 3:
        num = int(s, 16)
        rest = ""
    else:
        num = int(s[0:2], 16)
        rest = s[2:]
    return (num, rest)


def uuidMachineName(machine="", type=1):
    """Generates a universally unique name, including the machine name

    When using a type 4 id, the machine name is not taken into account as the uuid is completely random

    Args:
        machine (str, optional): hex string that defines a machine serial number. Defaults to "".
        type (int, optional): uuid type to use (1 is node dependant, 4 is completely random). Defaults to 1.

    Returns:
        str: universally unique name
    """
    if type == 4:
        id = str(uuid.uuid4())
    else:
        if machine == "":
            id = str(uuid.uuid1())
        else:
            id = str(uuid.uuid1(node=int(str(machine)[-12:], 16)))
    name = ""
    x = id.rsplit("-", 1)
    machine = x[1]
    x = x[0]
    x = x.replace("-", "")
    count = 0
    while len(x) > 0:
        tup = popHexPair(x)
        n = tup[0]
        if count >= random.randint(2, 4):  # nosec
            name += " "
            count = 0
        name += combos[n]
        count += 1
        x = tup[1]

    name += " "
    count = 0

    while len(machine) > 0:
        tup = popHexPair(machine)
        n = tup[0]
        if count == 3:
            name += " "
            count = 0
        name += combos[n]
        count += 1
        machine = tup[1]
    return name.title()


def uuidName():
    """Generates a universally unique name, without the machine unique part
    When used alone, this function can have collisions with other uuname generated on other machines.

    Returns:
        str: universally unique name, machine dependant
    """
    id = str(uuid.uuid1())
    name = ""
    x = id.rsplit("-", 1)
    x = x[0]
    x = x.replace("-", "")
    count = 0
    while len(x) > 0:
        tup = popHexPair(x)
        n = tup[0]
        if count >= random.randint(2, 4):  # nosec
            name += " "
            count = 0
        name += combos[n]
        count += 1
        x = tup[1]

    return name.title()


def machineName(machine=""):
    """Generates a machine name based on the same conversion mechanism as other functions in this module

    Args:
        machine (str, optional): hex string that defines a machine serial number. Defaults to "".

    Returns:
        str: machine name
    """
    if machine == "":
        machine = str(uuid.getnode())
    name = ""
    count = 0
    machine = machine[-12:]
    while len(machine) > 0:
        tup = popHexPair(machine)
        n = tup[0]
        if count == 3:
            name += " "
            count = 0
        name += combos[n]
        count += 1
        machine = tup[1]
    return name.title()


def getSerial():
    """Returns a serial number for the machine if run on a Raspberry Pi, otherwise a MAC address

    Returns:
        str: serial number or MAC address
    """
    if os.path.exists("/sys/firmware/devicetree/base/serial-number"):
        with open("/sys/firmware/devicetree/base/serial-number", "r") as serial_file:
            return serial_file.readline().strip("\x00")
    else:
        return str(uuid.getnode())


if __name__ == "__main__":
    print("Type 4:")
    print(uuidMachineName(type=4))
    print("Type 1:")
    print(uuidName())
    print(uuidMachineName())
    print(machineName())
    print(uuidMachineName(machine=getSerial()))
    print(machineName(machine=getSerial()))
    print(uuidMachineName(machine="10000000e108bd59"))
    print(machineName(machine="10000000e108bd59"))
