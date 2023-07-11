# Logger library compatible with multiprocessing
import sys
import os
import signal
import multiprocessing
import time
from loguru import logger
import planktoscope.mqtt
import planktoscope.stepper
import planktoscope.imager
import planktoscope.segmenter
import planktoscope.light
import planktoscope.uuidName
import planktoscope.display

# Configure the logger
logger.add(
    "PlanktoScope_{time}.log",
    rotation="5 MB",
    retention="1 week",
    compression=".tar.gz",
    enqueue=True,
    level="DEBUG",
)

# Set up a global variable for the main loop
run = True

def handler_stop_signals(signum, frame):
    """This handler simply stops the forever running loop in __main__"""
    global run
    logger.info(f"Received a signal asking to stop {signum}")
    run = False

if __name__ == "__main__":
    logger.info("Starting the PlanktoScope python script!")

    logger.info("Welcome!")
    logger.info("Initializing signals handling and sanitizing the directories (step 1/6)")
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Create script PID file
    with open('/tmp/pscope_pid', 'w') as f:
        f.write(str(os.getpid()))

    # Check GPU memory configuration
    with open("/boot/config.txt", "r") as config_file:
        for i, line in enumerate(config_file):
            if line.startswith("gpu_mem") and int(line.split("=")[1].strip()) < 256:
                logger.error("The GPU memory size is less than 256, this will prevent the camera from running properly")
                logger.error("Please edit the file /boot/config.txt to change the gpu_mem value to at least 256")
                logger.error("or use raspi-config to change the memory split, in menu 7 Advanced Options, A3 Memory Split")
                sys.exit(1)

    # Create directories if they don't exist
    img_path = "/home/pi/PlanktoScope/img"
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    export_path = "/home/pi/PlanktoScope/export"
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    logger.info(f"This PlanktoScope unique ID is {planktoscope.uuidName.getSerial()}")
    logger.info(f"This PlanktoScope unique name is {planktoscope.uuidName.machineName(machine=planktoscope.uuidName.getSerial())}")

    # Prepare the event for a graceful shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    # Start the stepper process for actuators
    logger.info("Starting the stepper control process (step 2/6)")
    stepper_thread = planktoscope.stepper.StepperProcess(shutdown_event)
    stepper_thread.start()

    # Start the imager control process
    logger.info("Starting the imager control process (step 3/6)")
    try:
        imager_thread = planktoscope.imager.ImagerProcess(shutdown_event)
    except:
        logger.error("The imager control process could not be started")
        imager_thread = None
    else:
        imager_thread.start()

    # Start the segmenter process
    logger.info("Starting the segmenter control process (step 4/6)")
    try:
        segmenter_thread = planktoscope.segmenter.SegmenterProcess(shutdown_event, "/home/pi/data")
    except Exception as e:
        logger.error("The segmenter control process could not be started")
        segmenter_thread = None
    else:
        segmenter_thread.start()

    # Start the light process
    logger.info("Starting the light control process (step 5/6)")
    try:
        light_thread = planktoscope.light.LightProcess(shutdown_event)
    except Exception as e:
        logger.error("The light control process could not be started")
        light_thread = None
    else:
        light_thread.start()

    # Start the module process
    # Uncomment here as needed
    # logger.info("Starting the module process")
    # module_thread = planktoscope.module.ModuleProcess(shutdown_event)
    # module_thread.start()

    logger.info("Starting the display control (step 6/6)")
    display = planktoscope.display.Display()

    logger.success("Looks like everything is set up and running, have fun!")

    while run:
        logger.trace("Running around in circles while waiting for someone to die!")
        if not stepper_thread.is_alive():
            logger.error("The stepper process died unexpectedly! Oh no!")
            break
        if not imager_thread or not imager_thread.is_alive():
            logger.error("The imager process died unexpectedly! Oh no!")
            break
        if not segmenter_thread or not segmenter_thread.is_alive():
            logger.error("The segmenter process died unexpectedly! Oh no!")
            break
        time.sleep(1)

    display.display_text("Bye Bye!")
    logger.info("Shutting down the shop")
    shutdown_event.set()
    time.sleep(1)

    stepper_thread.join()
    if imager_thread:
        imager_thread.join()
    if segmenter_thread:
        segmenter_thread.join()
    if light_thread:
        light_thread.join()
    # Uncomment this for clean shutdown
    # module_thread.join()

    stepper_thread.close()
    if imager_thread:
        imager_thread.close()
    if segmenter_thread:
        segmenter_thread.close()
    if light_thread:
        light_thread.close()
    # Uncomment this for clean shutdown
    # module_thread.close()

    display.stop()

    # Cleanup pid file
    os.remove('/tmp/pscope_pid')

    logger.info("Bye")
