import json
import multiprocessing
import signal
import time
from typing import Any

from loguru import logger

import focus
import pump
from imager import mqtt as imager

CONFIG_PATH_HARDWARE = "/home/pi/PlanktoScope/hardware.json"

logger.info("Starting the PlanktoScope python script!")

run = True  # global variable to enable clean shutdown from stop signals


def read_config(config_path: str) -> Any:
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


def handler_stop_signals(signum, frame):
    """This handler simply stop the forever running loop in __main__"""
    global run
    logger.info(f"Received a signal asking to stop {signum}")
    run = False


def main():
    logger.info("Initialising signals handling (step 1/4)")
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Prepare the event for a graceful shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    logger.info("Read hardware config")
    configuration = read_config(CONFIG_PATH_HARDWARE)

    # Starts the pump process
    logger.info("Starting the pump control process (step 2/4)")
    pump_thread = pump.PumpProcess(shutdown_event, configuration)
    pump_thread.start()

    # Starts the focus process
    logger.info("Starting the focus control process (step 3/4)")
    focus_thread = focus.FocusProcess(shutdown_event, configuration)
    focus_thread.start()

    # TODO try to isolate the imager thread (or another thread)
    # Starts the imager control process
    logger.info("Starting the imager control process (step 4/4)")
    imager_thread = imager.ImagerProcess(shutdown_event, configuration)
    imager_thread.start()

    logger.success("Looks like everything is set up and running, have fun!")

    while run:
        # TODO look into ways of restarting the dead threads
        logger.trace("Running around in circles while waiting for someone to die!")
        if pump_thread and not pump_thread.is_alive():
            logger.error("The pump process died unexpectedly! Oh no!")
            break
        if focus and not focus_thread.is_alive():
            logger.error("The focus process died unexpectedly! Oh no!")
            break
        if imager_thread and not imager_thread.is_alive():
            logger.error("The imager process died unexpectedly! Oh no!")
            break
        time.sleep(1)

    logger.info("Shutting down the shop")
    shutdown_event.set()
    time.sleep(1)

    if pump_thread:
        pump_thread.join()
    if focus_thread:
        focus_thread.join()
    if imager_thread:
        imager_thread.join()

    if pump_thread:
        pump_thread.close()
    if focus_thread:
        focus_thread.close()
    if imager_thread:
        imager_thread.close()

    logger.info("Bye")


if __name__ == "__main__":
    main()
