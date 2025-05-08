import typing

import loguru
import yaml

# TODO: instead check `~/PlanktoScope/config.json`'s `acq_instrument` field?
INSTALLER_CONFIG_FILE = "/usr/share/planktoscope/installer-config.yml"


def determine_variant(config_file: str):
    with open(config_file, "r") as file:
        variant: typing.Optional[str] = None
        try:
            config = yaml.safe_load(file)
            variant = config["hardware"]
            return variant
        except yaml.YAMLError:
            loguru.logger.exception(
                f"Couldn't parse {INSTALLER_CONFIG_FILE} as YAML file"
            )


def main():
    loguru.logger.info("Determining configured hardware variant...")
    variant = determine_variant(INSTALLER_CONFIG_FILE)
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
