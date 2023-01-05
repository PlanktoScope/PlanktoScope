# Copyright (C) 2021 Romain Bazile
# 
# This file is part of the PlanktoScope software.
# 
# PlanktoScope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PlanktoScope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PlanktoScope.  If not, see <http://www.gnu.org/licenses/>.

# Logger library compatible with multiprocessing
from loguru import logger
import sys

# multiprocessing module
import multiprocessing

# Time module so we can sleep
import time

# signal module is used to manage SINGINT/SIGTERM
import signal

# os module is used create paths
import os

# enqueue=True is necessary so we can log accross modules
# rotation happens everyday at 01:00 if not restarted
logger.add(
    # sys.stdout,
    "PlanktoScope_{time}.log",
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

# Library for exchaning messages with Node-RED
import planktoscope.mqtt

# Import the planktoscope stepper module
import planktoscope.stepper

# Import the planktoscope imager module
import planktoscope.imager

# Import the planktoscope segmenter module
import planktoscope.segmenter

# Import the planktoscope LED module
import planktoscope.light

# Import the planktoscope uuidName module
import planktoscope.uuidName

# Import the planktoscope display module for the OLED screen
import planktoscope.display

# global variable that keeps the wheels spinning
run = True


def handler_stop_signals(signum, frame):
    """This handler simply stop the forever running loop in __main__"""
    global run
    logger.info(f"Received a signal asking to stop {signum}")
    run = False


if __name__ == "__main__":
    logger.info("Welcome!")
    logger.info(
        "Initialising signals handling and sanitizing the directories (step 1/4)"
    )
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Create script PID file, so it's easy to kill the main process without ravaging all python script in the OS
    with open('/tmp/pscope_pid', 'w') as f:
        f.write(str(os.getpid()))
    
    # check if gpu_mem configuration is at least 256Meg, otherwise the camera will not run properly
    with open("/boot/config.txt", "r") as config_file:
        for i, line in enumerate(config_file):
            if line.startswith("gpu_mem") and int(line.split("=")[1].strip()) < 256:
                logger.error(
                    "The GPU memory size is less than 256, this will prevent the camera from running properly"
                )
                logger.error(
                    "Please edit the file /boot/config.txt to change the gpu_mem value to at least 256"
                )
                logger.error(
                    "or use raspi-config to change the memory split, in menu 7 Advanced Options, A3 Memory Split"
                )
                sys.exit(1)

    # Let's make sure the used base path exists
    img_path = "/home/pi/PlanktoScope/img"
    # check if this path exists
    if not os.path.exists(img_path):
        # create the path!
        os.makedirs(img_path)

    export_path = "/home/pi/PlanktoScope/export"
    # check if this path exists
    if not os.path.exists(export_path):
        # create the path!
        os.makedirs(export_path)

    logger.info(f"This PlanktoScope unique ID is {planktoscope.uuidName.getSerial()}")
    logger.info(
        f"This PlanktoScope unique name is {planktoscope.uuidName.machineName(machine=planktoscope.uuidName.getSerial())}"
    )

    # Prepare the event for a gracefull shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    # Starts the stepper process for actuators
    logger.info("Starting the stepper control process (step 2/4)")
    stepper_thread = planktoscope.stepper.StepperProcess(shutdown_event)
    stepper_thread.start()

    # Starts the imager control process
    logger.info("Starting the imager control process (step 3/4)")
    try:
        imager_thread = planktoscope.imager.ImagerProcess(shutdown_event)
    except:
        logger.error("The imager control process could not be started")
        imager_thread = None
    else:
        imager_thread.start()

    # Starts the segmenter process
    logger.info("Starting the segmenter control process (step 4/4)")
    try:
        segmenter_thread = planktoscope.segmenter.SegmenterProcess(
            shutdown_event, "/home/pi/data"
        )
    except Exception as e:
        logger.error("The segmenter control process could not be started")
        segmenter_thread = None
    else:
        segmenter_thread.start()

    # Starts the module process
    # Uncomment here as needed
    # logger.info("Starting the module process")
    # module_thread = planktoscope.module.ModuleProcess(shutdown_event)
    # module_thread.start()

    logger.info("Starting the display module")
    display = planktoscope.display.Display()

    logger.success("Looks like everything is set up and running, have fun!")
    planktoscope.light.ready()

    while run:
        # TODO look into ways of restarting the dead threads
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
    # Uncomment this for clean shutdown
    # module_thread.join()

    stepper_thread.close()
    if imager_thread:
        imager_thread.close()
    if segmenter_thread:
        segmenter_thread.close()
    # Uncomment this for clean shutdown
    # module_thread.close()

    display.stop()

    # Cleanup pid file
    os.remove('/tmp/pscope_pid')
    
    logger.info("Bye")
