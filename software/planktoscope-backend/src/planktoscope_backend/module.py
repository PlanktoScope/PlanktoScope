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

################################################################################
# Practical Libraries
################################################################################
# Logger library compatible with multiprocessing
from loguru import logger

import os, time

# Library for starting processes
import multiprocessing

# Basic planktoscope communication libraries
import planktoscope.mqtt

logger.info("planktoscope.module is loaded")

################################################################################
# Main Segmenter class
################################################################################
class ModuleProcess(multiprocessing.Process):
    """This class contains the main definitions for the module of the PlanktoScope"""

    @logger.catch
    def __init__(self, event):
        """Initialize the Module class

        Args:
            event (multiprocessing.Event): shutdown event
        """
        super(ModuleProcess, self).__init__(name="light")

        logger.info("planktoscope.module is initialising")

        # Do all your initialisation here

        logger.success("planktoscope.mdule is initialised and ready to go!")

    @logger.catch
    def treat_message(self):
        action = ""
        if self.module_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.module_client.msg["payload"]
            logger.debug(last_message)
            self.module_client.read_message()
            if "action" not in last_message:
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.module_client.client.publish("status/module", '{"status":"Error"}')
                return
            action = last_message["action"]
        if action == "on":
            # Treat the received messages here
            pass
        elif action != "":
            logger.warning(
                f"We did not understand the received request {action} - {last_message}"
            )

    ################################################################################
    # While loop for capturing commands from Node-RED
    ################################################################################
    @logger.catch
    def run(self):
        """This is the function that needs to be started to create a thread"""
        logger.info(
            f"The module control thread has been started in process {os.getpid()}"
        )

        # MQTT Service connection
        self.module_client = planktoscope.mqtt.MQTT_Client(
            topic="module/#", name="module_client"
        )

        # Publish the status "Ready" to via MQTT to Node-RED
        self.module_client.client.publish("status/module", '{"status":"Ready"}')

        logger.success("Module is READY!")

        # This is the loop
        while not self.stop_event.is_set():
            self.treat_message()
            time.sleep(0.1)

        logger.info("Shutting down the module process")
        # Do your deinit and ressources cleanup here
        self.module_client.client.publish("status/module", '{"status":"Dead"}')
        self.module_client.shutdown()
        logger.success("Module process shut down! See you!")


# This is called if this script is launched directly
if __name__ == "__main__":
    # This should be tests of your module
    pass
