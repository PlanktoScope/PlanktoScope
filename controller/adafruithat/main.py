# Copyright Romain Bazile and other PlanktoScope project contributors
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

import multiprocessing
import time
import signal  # for handling SIGINT/SIGTERM

from loguru import logger  # for logging with multiprocessing

from . import stepper, light
from .display import Display
from imager import mqtt as imager

logger.info("Starting the PlanktoScope hardware controller!")

run = True  # global variable to enable clean shutdown from stop signals


def handler_stop_signals(signum, _):
    """This handler simply stop the forever running loop in __main__"""
    global run
    logger.info(f"Received a signal asking to stop {signum}")
    run = False


def main(configuration):
    logger.info("Initialising signals handling (step 1/4)")
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Prepare the event for a graceful shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    # Starts the stepper process for actuators
    logger.info("Starting the stepper control process (step 2/4)")
    stepper_thread = stepper.StepperProcess(shutdown_event)
    stepper_thread.start()

    # Starts the imager control process
    logger.info("Starting the imager control process (step 3/4)")
    imager_thread = None
    try:
        imager_thread = imager.ImagerProcess(shutdown_event, configuration)
        imager_thread.start()
    except Exception as e:
        logger.error(f"The imager control process could not be started: {e}")

    logger.info("Starting the display module (step 4/4)")
    display = Display()

    logger.success("Looks like the controller is set up and running, have fun!")
    light.ready()

    while run:
        # TODO look into ways of restarting the dead threads
        logger.trace("Running around in circles while waiting for someone to die!")
        if not stepper_thread.is_alive():
            logger.error("The stepper process died unexpectedly! Oh no!")
            break
        if not imager_thread or not imager_thread.is_alive():
            logger.error("The imager process died unexpectedly! Oh no!")
            break
        time.sleep(1)

    display.display_text("Bye Bye!")
    logger.info("Shutting down...")
    shutdown_event.set()
    time.sleep(1)

    stepper_thread.join()
    if imager_thread:
        imager_thread.join()

    stepper_thread.close()
    if imager_thread:
        imager_thread.close()

    display.stop()

    logger.info("Bye!")
