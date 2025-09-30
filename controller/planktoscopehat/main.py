import multiprocessing
import time
import signal

from loguru import logger

from . import pump, focus
from imager import mqtt as imager

logger.info("Starting the PlanktoScope python script!")

run = True  # global variable to enable clean shutdown from stop signals


def handler_stop_signals(signum, frame):
    """This handler simply stop the forever running loop in __main__"""
    global run
    logger.info(f"Received a signal asking to stop {signum}")
    run = False


def main(configuration):
    logger.info("Initialising signals handling (step 1/5)")
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Prepare the event for a graceful shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    # Starts the pump process
    logger.info("Starting the pump control process (step 2/5)")
    pump_thread = pump.PumpProcess(shutdown_event, configuration)
    pump_thread.start()

    # Starts the focus process
    logger.info("Starting the focus control process (step 3/5)")
    focus_thread = focus.FocusProcess(shutdown_event, configuration)
    focus_thread.start()

    # TODO try to isolate the imager thread (or another thread)
    # Starts the imager control process
    logger.info("Starting the imager control process (step 4/5)")
    imager_thread = None
    try:
        imager_thread = imager.ImagerProcess(shutdown_event, configuration)
        imager_thread.start()
    except Exception as e:
        logger.error(f"The imager control process could not be started: {e}")

    # Starts the light process
    logger.info("Starting the light control process (step 5/5)")
    hat_version = float(configuration.get("hat_version") or 0)
    if hat_version < 3.1:
        from . import light_v26 as light
    else:
        from . import light_v30 as light

    light_thread = None
    try:
        light_thread = light.LightProcess(shutdown_event, configuration)
        light_thread.start()
    except Exception:
        logger.error("The light control process could not be started")

    logger.success("Looks like everything is set up and running, have fun!")

    while run:
        # TODO look into ways of restarting the dead threads
        logger.trace("Running around in circles while waiting for someone to die!")
        if not pump_thread.is_alive():
            logger.error("The pump process died unexpectedly! Oh no!")
            break
        if not focus_thread.is_alive():
            logger.error("The focus process died unexpectedly! Oh no!")
            break
        if not imager_thread or not imager_thread.is_alive():
            logger.error("The imager process died unexpectedly! Oh no!")
            break
        # if not light_thread or not light_thread.is_alive():
        #     logger.error("The light process died unexpectedly! Oh no!")
        #     break
        time.sleep(1)

    logger.info("Shutting down the shop")
    shutdown_event.set()
    time.sleep(1)

    pump_thread.join()
    focus_thread.join()
    if imager_thread:
        imager_thread.join()
    # if light_thread:
    #     light_thread.join()

    pump_thread.close()
    focus_thread.close()
    if imager_thread:
        imager_thread.close()
    # if light_thread:
    #     light_thread.close()

    logger.info("Bye")
