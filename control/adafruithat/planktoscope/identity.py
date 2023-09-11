# TODO: keep this as the default path, but allow changing it with an environment variable
MACHINE_NAME_PATH = '/home/pi/.local/etc/machine-name'

def load_machine_name(path=MACHINE_NAME_PATH):
    """Returns the machine name specified by the file at MACHINE_NAMEPATH.

    Returns:
        str: the machine name stored in the file at the path.
    """
    with open(path, encoding='utf-8') as file:
        return file.readline().strip()
