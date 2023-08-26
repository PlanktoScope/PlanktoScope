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
import os

from loguru import logger  # for logging with multiprocessing

import planktoscope.mqtt
import planktoscope.segmenter

# enqueue=True is necessary so we can log accross modules
# rotation happens everyday at 01:00 if not restarted
logger.add(
    "PlanktoScope-processing-segmenter_{time}.log",
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

logger.info("Starting the PlanktoScope data processing segmenter!")

run = True  # global variable to enable clean shutdown from stop signals

def handler_stop_signals(signum, _):
    """This handler simply stop the forever running loop in __main__"""
    global run
    logger.info(f"Received a signal asking to stop {signum}")
    run = False


if __name__ == "__main__":
    logger.info("Welcome!")
    logger.info( "Initialising signals handling and sanitizing the directories (step 1/2)")
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Create script PID file, so it's easy to kill the main process without ravaging all python script in the OS
    # TODO: don't make a PID file - supervise with systemd or Docker instead
    with open('/tmp/planktoscope-processing-segmenter_pid', 'w') as f:
        f.write(str(os.getpid()))

    export_path = "/home/pi/PlanktoScope/export"  # FIXME: this path is incorrect - why doesn't it cause side effects?
    # check if this path exists
    if not os.path.exists(export_path):
        # create the path!
        os.makedirs(export_path)

    # Prepare the event for a graceful shutdown
    shutdown_event = multiprocessing.Event()
    shutdown_event.clear()

    # Starts the segmenter process
    logger.info("Starting the segmenter control process (step 2/2)")
    try:
        segmenter_thread = planktoscope.segmenter.SegmenterProcess(shutdown_event, "/home/pi/data")
    except Exception as e:
        logger.error("The segmenter control process could not be started")
        segmenter_thread = None
    else:
        segmenter_thread.start()

    logger.success("Looks like the segmenter is set up and running, have fun!")

    while run:
        # TODO look into ways of restarting the dead threads
        logger.trace("Running around in circles while waiting for someone to die!")
        if not segmenter_thread or not segmenter_thread.is_alive():
            logger.error("The segmenter process died unexpectedly! Oh no!")
            break
        time.sleep(1)

    logger.info("Shutting down...")
    shutdown_event.set()
    time.sleep(1)

    if segmenter_thread:
        segmenter_thread.join()

    if segmenter_thread:
        segmenter_thread.close()

    os.remove('/tmp/planktoscope-processing-segmenter_pid')
    logger.info("Bye!")
