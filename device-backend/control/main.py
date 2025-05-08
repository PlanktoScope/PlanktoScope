import typing

import loguru
import yaml

# FIXME: move loguru configuration to here instead


def load_variant_setting(config_file: str):
    config = {}
    try:
        with open(config_file, "r") as file:
            try:
                config = yaml.safe_load(file)
            except Exception:
                loguru.logger.exception(f"Couldn't parse {config_file} as YAML file")
                return None
    except Exception:
        loguru.logger.exception(f"Couldn't open {config_file}")
        return None

    variant: typing.Optional[str] = None
    try:
        variant = config["hardware"]
    except Exception:
        loguru.logger.error(f"{config_file} lacks a 'hardware' field")
        return None

    if variant == "fairscope-latest":
        return "planktoscopehat"

    return variant


# TODO: instead check `~/PlanktoScope/config.json`'s `acq_instrument` field?
INSTALLER_CONFIG_FILE = "/usr/share/planktoscope/installer-config.yml"


def main():
    loguru.logger.info("Determining configured hardware variant...")
    variant = load_variant_setting(INSTALLER_CONFIG_FILE)
    if variant is None:
        variant = "planktoscopehat"
        loguru.logger.warning(
            f"Couldn't load hardware variant setting, defaulting to {variant}"
        )
    loguru.logger.info(f"Hardware variant: {variant}")
    # Note: once the `main.py` files are rewritten to have a main() function, we can import the
    # appropriate module and invoke its main function. For now, we have to do an `exec`:
    with open(f"{variant}/main.py") as script:
        exec(script.read())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        loguru.logger.exception("Unhandled exception")
