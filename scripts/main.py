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

# Starts the stepper process for actuators
logger.info("Starting the stepper control process")
stepper_thread = planktoscope.stepper.StepperProcess()
stepper_thread.start()

# Streaming server creation
output = planktoscope.streamer.StreamingOutput()
address = ("", 8000)
server = planktoscope.streamer.StreamingServer(
    address, planktoscope.streamer.StreamingHandler
)

# Starts the streaming server process
logger.info("Starting the streaming server process")
streaming_thread = multiprocessing.Process(target=server.serve_forever)
streaming_thread.start()

# Starts the imager control process
logger.info("Starting the imager control process")
imager_thread = planktoscope.imager.ImagerProcess()
imager_thread.start_camera(output)
imager_thread.start()

while True:
    pass