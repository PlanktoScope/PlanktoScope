import sys
import multiprocessing
import time
import signal
import os
import json

from loguru import logger

import planktoscope.mqtt
import planktoscope.pump
import planktoscope.focus
import planktoscope.light
import planktoscope.identity
from planktoscope.imager import mqtt as imager

# enqueue=True is necessary so we can log across modules
# rotation happens everyday at 01:00 if not restarted
logs_path = "/home/pi/device-backend-logs/control"
if not os.path.exists(logs_path):
    os.makedirs(logs_path)
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

logger.info("Starting the PlanktoScope python script!")

run = True  # global variable to enable clean shutdown from stop signals


def handler_stop_signals(signum, frame):
    """This handler simply stop the forever running loop in __main__"""
    global run
    logger.info(f"Received a signal asking to stop {signum}")
    run = False


if __name__ == "__main__":
    logger.info("Welcome!")
    logger.info(
        "Initialising configuration, signals handling and sanitizing the directories (step 1/5)"
    )
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

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

    # Let's make sure the used base path exists
    img_path = "/home/pi/img"
    # check if this path exists
    if not os.path.exists(img_path):
        # create the path!
        os.makedirs(img_path)

    logger.info(
        f"This PlanktoScope's machine name is {planktoscope.identity.load_machine_name()}"
    )

    try:
        with open("/home/pi/PlanktoScope/hardware.json", "r") as config_file:
            configuration = json.load(config_file)
    except FileNotFoundError:
        logger.info(
            "The hardware configuration file doesn't exists, using defaults"
        )
        configuration = {}

    # Prepare the event for a graceful shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    # Starts the pump process
    logger.info("Starting the pump control process (step 2/5)")
    pump_thread = planktoscope.pump.PumpProcess(shutdown_event, configuration)
    pump_thread.start()

    # Starts the focus process
    logger.info("Starting the focus control process (step 3/5)")
    focus_thread = planktoscope.focus.FocusProcess(shutdown_event, configuration)
    focus_thread.start()

    # TODO try to isolate the imager thread (or another thread)
    # Starts the imager control process
    logger.info("Starting the imager control process (step 4/5)")
    try:
        imager_thread = imager.Worker(shutdown_event, configuration)
    except Exception as e:
        logger.error(f"The imager control process could not be started: {e}")
        imager_thread = None
    else:
        imager_thread.start()

    # Starts the light process
    logger.info("Starting the light control process (step 5/5)")
    try:
        light_thread = planktoscope.light.LightProcess(shutdown_event, configuration)
    except Exception:
        logger.error("The light control process could not be started")
        light_thread = None
    else:
        light_thread.start()

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
        time.sleep(1)

    logger.info("Shutting down the shop")
    shutdown_event.set()
    time.sleep(1)

    pump_thread.join()
    focus_thread.join()
    if imager_thread:
        imager_thread.join()
    if light_thread:
        light_thread.join()

    pump_thread.close()
    focus_thread.close()
    if imager_thread:
        imager_thread.close()
    if light_thread:
        light_thread.close()

    logger.info("Bye")
