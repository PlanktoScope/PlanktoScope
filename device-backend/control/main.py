import json
from os import makedirs, path

from loguru import logger

# enqueue=True is necessary so we can log across modules
# rotation happens everyday at 01:00 if not restarted
logs_path = "/home/pi/device-backend-logs/control"
if not path.exists(logs_path):
    makedirs(logs_path)
logger.add(
    # sys.stdout,
    "/home/pi/device-backend-logs/control/{time}.log",
    rotation="5 MB",
    retention="1 week",
    compression=".tar.gz",
    enqueue=True,
    level="DEBUG",
)

# The available level for the logger are as follows:
# Level name 	Severity 	Logger method
# TRACE 	    5 	        logger.trace()
# DEBUG 	    10 	        logger.debug()
# INFO 	        20 	        logger.info()
# SUCCESS 	    25 	        logger.success()
# WARNING 	    30      	logger.warning()
# ERROR 	    40       	logger.error()
# CRITICAL 	    50      	logger.critical()

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
                logger.exception(f"Couldn't parse {config_path} as JSON file")
                return None
    except Exception:
        logger.exception(f"Couldn't open {config_path}")
        return None

    if "acq_instrument" not in config:
        logger.error(f"{config_path} lacks a 'acq_instrument' field")
        return None

    if config["acq_instrument"] == "PlanktoScope v2.1":
        return "adafruithat"
    return "planktoscopehat"


def main():
    logger.info("Determining configured hardware variant...")
    variant = load_variant_setting()
    if variant is None:
        variant = "planktoscopehat"
        logger.warning(
            f"Couldn't load hardware variant setting from config, defaulting to {variant}"
        )
    logger.info(f"Hardware variant: {variant}")

    if variant == "adafruithat":
        from adafruithat import main as platform  # noqa: IMR200
    else:
        from planktoscopehat import main as platform  # noqa: IMR200

    platform.main()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled exception")
