import json
from os import path

import loguru

# FIXME: move loguru configuration to here instead


HARDWARE_VARIANTS = {
    "PlanktoScope v2.1": "adafruithat",
    "PlanktoScope v2.3": "planktoscopehat",
    "PlanktoScope v2.5": "planktoscopehat",
    "PlanktoScope v2.6": "planktoscopehat",
    "PlanktoScope v3.0": "planktoscopehat",
    # Note: null is the default version value for planktoscopehat-latest.config.json; see
    # https://github.com/PlanktoScope/PlanktoScope/pull/432 for details.
    None: "planktoscopehat",
}


def load_variant_setting(config_path: str):
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

    return HARDWARE_VARIANTS.get(config["acq_instrument"], None)


CONFIG_PATH = path.join(
    path.dirname(path.dirname(path.dirname(__file__))),
    "config.json",
)


def main():
    loguru.logger.info("Determining configured hardware variant...")
    variant = load_variant_setting(CONFIG_PATH)
    if variant is None:
        variant = "planktoscopehat"
        loguru.logger.warning(
            f"Couldn't load hardware variant setting from config, defaulting to {variant}"
        )
    loguru.logger.info(f"Hardware variant: {variant}")
    # Note: once the `main.py` files are rewritten to have a main() function, we can import the
    # appropriate module and invoke its main function. For now, we have to do an `exec`:
    script_path = path.join(path.dirname(__file__), variant, "main.py")
    with open(script_path) as script:
        exec(script.read())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        loguru.logger.exception("Unhandled exception")
