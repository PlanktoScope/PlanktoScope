import json
from typing import Any

from . import mqtt as imager

CONFIG_PATH_HARDWARE = "/home/pi/PlanktoScope/hardware.json"


def read_config(config_path: str) -> Any:
    config = {}
    try:
        with open(config_path, "r") as file:
            try:
                config = json.load(file)
            except Exception:
                return None
    except Exception:
        return None

    return config


def main():
    configuration = read_config(CONFIG_PATH_HARDWARE)
    imager_thread = imager.Imager(configuration)
    imager_thread.run()


if __name__ == "__main__":
    main()
