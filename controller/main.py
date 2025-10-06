import json
from typing import Any
import sys

from loguru import logger

# This is a special case for legacy hardware; new hardware designs should all be part of the
# planktoscopehat codebase:
CONFIG_PATH = "/home/pi/PlanktoScope/config.json"


def read_config(config_path: str = CONFIG_PATH) -> Any:
    config = {}
    try:
        with open(config_path, "r") as file:
            try:
                config = json.load(file)
            except Exception:
                logger.exception(f"Couldn't parse {config_path} as JSON file")
                return None
    except Exception:
        logger.exception(f"Couldn't open {config_path}")
        return None

    return config


def get_variant(config: dict[str, Any]) -> str | None:
    if config is None:
        return None

    if "acq_instrument" not in config:
        logger.error("config lacks a 'acq_instrument' field")
        return None

    if config["acq_instrument"] == "PlanktoScope v2.1":
        return "adafruithat"
    return "planktoscopehat"


def main():
    logger.info("Welcome!")

    # check if gpu_mem configuration is at least 256Meg, otherwise the camera will not run properly
    with open("/boot/firmware/config.txt", "r") as config_file:
        for i, line in enumerate(config_file):
            if line.startswith("gpu_mem") and int(line.split("=")[1].strip()) < 256:
                logger.error(
                    "The GPU memory size is less than 256, this will prevent the camera from running properly"
                )
                logger.error(
                    "Please edit the file /boot/firmware/config.txt to change the gpu_mem value to at least 256"
                )
                logger.error(
                    "or use raspi-config to change the memory split, in menu 7 Advanced Options, A3 Memory Split"
                )
                sys.exit(1)

    logger.info("Determining configured hardware variant...")
    config = read_config(CONFIG_PATH)
    variant = get_variant(config)
    if variant is None:
        variant = "planktoscopehat"
        logger.warning(
            f"Couldn't load hardware variant setting from config, defaulting to {variant}"
        )
    logger.info(f"Hardware variant: {variant}")

    if variant == "adafruithat":
        from adafruithat import main as platform
    else:
        from planktoscopehat import main as platform

    platform.main(config)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled exception")
