import json
from os import path

import loguru

# FIXME: move loguru configuration to here instead

# This is a special case for legacy hardware; new hardware designs should all be part of the
# planktoscopehat codebase:
CONFIG_PATH = "/home/pi/PlanktoScope/config.json"
def load_variant_setting(config_path: str = CONFIG_PATH):
    config = {}
    try:
        with open(config_path, "r") as file:
            try:
                config = json.load(file)
            except Exception:
                loguru.logger.exception(f"Couldn't parse {config_path} as JSON file")
                return None
    except Exception:
        loguru.logger.exception(f"Couldn't open {config_path}")
        return None

    if "acq_instrument" not in config:
        loguru.logger.error(f"{config_path} lacks a 'acq_instrument' field")
        return None

    if config["acq_instrument"] == "PlanktoScope v2.1":
        return "adafruithat"
    return "planktoscopehat"

def main():
    loguru.logger.info("Determining configured hardware variant...")
    variant = load_variant_setting()
    if variant is None:
        variant = "planktoscopehat"
        loguru.logger.warning(
            f"Couldn't load hardware variant setting from config, defaulting to {variant}"
        )
    loguru.logger.info(f"Hardware variant: {variant}")
    # Note: once the `main.py` files are rewritten to have a main() function, we can import the
    # appropriate module and invoke its main function. For now, we have to do an `exec`:
    # script_path = path.join(path.dirname(__file__), variant, "main.py")
    # with open(script_path) as script:
        # exec(script.read())

    if variant == "adafruithat":
       from adafruithat import main as platform
    else:
        from planktoscopehat import main as platform

    platform.main()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        loguru.logger.exception("Unhandled exception")
