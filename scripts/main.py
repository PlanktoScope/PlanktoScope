# Logger library compatible with multiprocessing
from loguru import logger
import sys

# enqueue=True is necessary so we can log accross modules
# rotation happens everyday at 01:00 if not restarted
logger.add(
    # sys.stdout,
    "PlanktoScope_{time}.log",
    rotation="01:00",
    retention="1 month",
    compression=".tar.gz",
    enqueue=True,
    level="INFO",
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

# Library for exchaning messages with Node-RED
import planktoscope.mqtt

# Import the planktonscope stepper module
import planktoscope.stepper

# Import the planktonscope LED module
import planktoscope.light

# Time module so we can sleep
import time

# signal module is used to managed SINGINT/SIGTERM
import signal

# global variable that keeps the wheels spinning
run = True


def handler_stop_signals(signum, frame):
    """This handler simply stop the forever running loop in __main__"""
    global run
    run = False


if __name__ == "__main__":
    logger.info("Starting up the PlanktoScope management script")
    logger.info("Welcome!")

    logger.info("Initialising signals handling (step 1/4)")
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Prepare the event for a gracefull shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    # Starts the stepper process for actuators
    logger.info("Starting the stepper control process (step 2/4)")
    stepper_thread = planktoscope.stepper.StepperProcess(shutdown_event)
    stepper_thread.start()

    # Streaming server creation
    output = planktoscope.streamer.StreamingOutput()
    address = ("", 8000)
    server = planktoscope.streamer.StreamingServer(
        address, planktoscope.streamer.StreamingHandler
    )

    # Starts the streaming server process
    logger.info("Starting the streaming server process (step 3/4)")
    streaming_thread = multiprocessing.Process(target=server.serve_forever)
    streaming_thread.start()

    # Starts the imager control process
    logger.info("Starting the imager control process (step 4/4)")
    imager_thread = planktoscope.imager.ImagerProcess()
    imager_thread.start_camera(output)
    imager_thread.start()

    logger.info("Looks like everything is set up and running, have fun!")

    while run:
        # TODO implement checks on the different processes started before
        # If they are not alive, we need to restart them
        logger.trace("Running around in circles while waiting for someone to die!")
        if not stepper_thread.is_alive():
            logger.error("The stepper process died unexpectedly! Oh no!")
        if not streaming_thread.is_alive():
            logger.error("The streaming process died unexpectedly! Oh no!")
        if not imager_thread.is_alive():
            logger.error("The imager process died unexpectedly! Oh no!")
        time.sleep(1)

    logger.info("Shutting down the shop")
    shutdown_event.set()
    stepper_thread.join()
    streaming_thread.terminate()
    imager_thread.join()
    logger.info("Bye")