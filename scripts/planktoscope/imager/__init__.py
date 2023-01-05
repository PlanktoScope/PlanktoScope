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

# Library to get date and time for folder name and filename
import datetime

# Library to be able to sleep for a given duration
import time

# Libraries manipulate json format, execute bash commands
import json

# Library for path and filesystem manipulations
import os
import shutil

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import planktoscope.mqtt
import planktoscope.light

# import planktoscope.streamer
import planktoscope.imager.state_machine

# import raspimjpeg module
import planktoscope.imager.raspimjpeg

# import streamer module
import planktoscope.imager.streamer

# Integrity verification module
import planktoscope.integrity

# Uuid module
import planktoscope.uuidName


# Libraries for the streaming server
import threading
import functools


logger.info("planktoscope.imager is loaded")

################################################################################
# Main Imager class
################################################################################
class ImagerProcess(multiprocessing.Process):
    """This class contains the main definitions for the imager of the PlanktoScope"""

    def __init__(self, stop_event, iso=100, shutter_speed=1):
        """Initialize the Imager class

        Args:
            stop_event (multiprocessing.Event): shutdown event
            iso (int, optional): ISO sensitivity. Defaults to 100.
            shutter_speed (int, optional): Shutter speed of the camera. Defaults to 500.
        """
        super(ImagerProcess, self).__init__(name="imager")

        logger.info("planktoscope.imager is initialising")

        if os.path.exists("/home/pi/PlanktoScope/hardware.json"):
            # load hardware.json
            with open("/home/pi/PlanktoScope/hardware.json", "r") as config_file:
                configuration = json.load(config_file)
                logger.debug(f"Hardware configuration loaded is {configuration}")
        else:
            logger.info(
                "The hardware configuration file doesn't exists, using defaults"
            )
            configuration = {}

        self.__camera_type = "v2.1"

        # parse the config data. If the key is absent, we are using the default value
        self.__camera_type = configuration.get("camera_type", self.__camera_type)

        self.stop_event = stop_event
        self.__imager = planktoscope.imager.state_machine.Imager()
        self.__img_goal = 0
        self.__img_done = 0
        self.__sleep_before = None
        self.__pump_volume = None
        self.__pump_direction = "FORWARD"
        self.__img_goal = None
        self.imager_client = None
        self.__error = 0

        # Initialise the camera and the process
        # Also starts the streaming to the temporary file
        self.__camera = planktoscope.imager.raspimjpeg.raspimjpeg()

        try:
            self.__camera.start()
        except Exception as e:
            logger.exception(
                f"An exception has occured when starting up raspimjpeg: {e}"
            )
            try:
                self.__camera.start(True)
            except Exception as e:
                logger.exception(
                    f"A second exception has occured when starting up raspimjpeg: {e}"
                )
                logger.error("This error can't be recovered from, terminating now")
                raise e

        if self.__camera.sensor_name == "IMX219":  # Camera v2.1
            self.__resolution = (3280, 2464)
        elif self.__camera.sensor_name == "IMX477":  # Camera HQ
            self.__resolution = (4056, 3040)
        else:
            self.__resolution = (1280, 1024)
            logger.error(
                f"The connected camera {self.__camera.sensor_name} is not recognized, please check your camera"
            )

        self.__iso = iso
        self.__shutter_speed = shutter_speed
        self.__exposure_mode = "auto"
        self.__white_balance = "off"
        self.__white_balance_gain = (
            int(configuration.get("red_gain", 2.00) * 100),
            int(configuration.get("blue_gain", 1.40) * 100),
        )
        self.__image_gain = (
            int(configuration.get("analog_gain", 1.00) * 100),
            int(configuration.get("digital_gain", 1.00) * 100),
        )

        self.__base_path = "/home/pi/data/img"
        # Let's make sure the base path exists
        if not os.path.exists(self.__base_path):
            os.makedirs(self.__base_path)

        self.__export_path = ""
        self.__global_metadata = None

        logger.info("Initialising the camera with the default settings")
        try:
            self.__camera.resolution = self.__resolution
        except TimeoutError as e:
            logger.error(
                "A timeout has occured when setting the resolution, trying again"
            )
            self.__camera.resolution = self.__resolution
        time.sleep(0.1)

        try:
            self.__camera.iso = self.__iso
        except TimeoutError as e:
            logger.error(
                "A timeout has occured when setting the ISO number, trying again"
            )
            self.__camera.iso = self.__iso
        time.sleep(0.1)

        try:
            self.__camera.shutter_speed = self.__shutter_speed
        except TimeoutError as e:
            logger.error(
                "A timeout has occured when setting the shutter speed, trying again"
            )
            self.__camera.shutter_speed = self.__shutter_speed
        time.sleep(0.1)

        try:
            self.__camera.exposure_mode = self.__exposure_mode
        except TimeoutError as e:
            logger.error(
                "A timeout has occured when setting the exposure mode, trying again"
            )
            self.__camera.exposure_mode = self.__exposure_mode
        time.sleep(0.1)

        try:
            self.__camera.white_balance = self.__white_balance
        except TimeoutError as e:
            logger.error(
                "A timeout has occured when setting the white balance mode, trying again"
            )
            self.__camera.white_balance = self.__white_balance
        time.sleep(0.1)

        try:
            self.__camera.white_balance_gain = self.__white_balance_gain
        except TimeoutError as e:
            logger.error(
                "A timeout has occured when setting the white balance gain, trying again"
            )
            self.__camera.white_balance_gain = self.__white_balance_gain
        time.sleep(0.1)

        try:
            self.__camera.image_gain = self.__image_gain
        except TimeoutError as e:
            logger.error(
                "A timeout has occured when setting the white balance gain, trying again"
            )
            self.__camera.image_gain = self.__image_gain

        logger.success("planktoscope.imager is initialised and ready to go!")

    def __message_image(self, last_message):
        """Actions for when we receive a message"""
        if (
            "sleep" not in last_message
            or "volume" not in last_message
            or "nb_frame" not in last_message
            or "pump_direction" not in last_message
        ):
            logger.error(f"The received message has the wrong argument {last_message}")
            self.imager_client.client.publish("status/imager", '{"status":"Error"}')
            return
        self.__imager.change(planktoscope.imager.state_machine.Imaging)

        # Get duration to wait before an image from the different received arguments
        self.__sleep_before = float(last_message["sleep"])

        # Get volume in between two images from the different received arguments
        self.__pump_volume = float(last_message["volume"])

        # Get the pump direction message
        self.__pump_direction = last_message["pump_direction"]

        # Get the number of frames to image from the different received arguments
        self.__img_goal = int(last_message["nb_frame"])

        # Reset the counter to 0
        self.__img_done = 0

        self.imager_client.client.publish("status/imager", '{"status":"Started"}')

    def __message_stop(self):
        self.imager_client.client.unsubscribe("status/pump")

        # Stops the pump
        self.imager_client.client.publish("actuator/pump", '{"action": "stop"}')

        logger.info("The imaging has been interrupted.")

        # Publish the status "Interrupted" to via MQTT to Node-RED
        self.imager_client.client.publish("status/imager", '{"status":"Interrupted"}')

        planktoscope.light.interrupted()

        self.__imager.change(planktoscope.imager.state_machine.Stop)

    def __message_update(self, last_message):
        if self.__imager.state.name == "stop":
            if "config" not in last_message:
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.imager_client.client.publish(
                    "status/imager", '{"status":"Configuration message error"}'
                )
                return

            logger.info("Updating the configuration now with the received data")
            # Updating the configuration with the passed parameter in payload["config"]
            self.__global_metadata = last_message["config"]

            # Publish the status "Config updated" to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/imager", '{"status":"Config updated"}'
            )
            logger.info("Configuration has been updated")
        else:
            logger.error("We can't update the configuration while we are imaging.")
            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.imager_client.client.publish("status/imager", '{"status":"Busy"}')

    def __message_settings(self, last_message):
        # TODO simplify this method, move timeout error check inside self.__camera.resolution/iso/etc.
        if self.__imager.state.name == "stop":
            if "settings" not in last_message:
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.imager_client.client.publish(
                    "status/imager", '{"status":"Camera settings error"}'
                )
                return
            logger.info("Updating the camera settings now with the received data")
            # Updating the configuration with the passed parameter in payload["config"]
            settings = last_message["settings"]
            if "resolution" in settings:
                self.__resolution = settings.get("resolution", self.__resolution)
                logger.debug(f"Updating the camera resolution to {self.__resolution}")
                try:
                    self.__camera.resolution = self.__resolution
                except TimeoutError as e:
                    logger.error(
                        "A timeout has occured when setting the resolution, trying again"
                    )
                    self.__camera.resolution = self.__resolution
                except ValueError as e:
                    logger.error("The requested resolution is not valid!")
                    self.imager_client.client.publish(
                        "status/imager", '{"status":"Error: Resolution not valid"}'
                    )
                    return

            if "iso" in settings:
                self.__iso = settings.get("iso", self.__iso)
                logger.debug(f"Updating the camera iso to {self.__iso}")
                try:
                    self.__camera.iso = self.__iso
                except TimeoutError as e:
                    logger.error(
                        "A timeout has occured when setting the ISO number, trying again"
                    )
                    self.__camera.iso = self.__iso
                except ValueError as e:
                    logger.error("The requested ISO number is not valid!")
                    self.imager_client.client.publish(
                        "status/imager", '{"status":"Error: Iso number not valid"}'
                    )
                    return

            if "shutter_speed" in settings:
                self.__shutter_speed = settings.get(
                    "shutter_speed", self.__shutter_speed
                )
                logger.debug(
                    f"Updating the camera shutter speed to {self.__shutter_speed}"
                )
                try:
                    self.__camera.shutter_speed = self.__shutter_speed
                except TimeoutError as e:
                    logger.error(
                        "A timeout has occured when setting the shutter speed, trying again"
                    )
                    self.__camera.shutter_speed = self.__shutter_speed
                except ValueError as e:
                    logger.error("The requested shutter speed is not valid!")
                    self.imager_client.client.publish(
                        "status/imager", '{"status":"Error: Shutter speed not valid"}'
                    )
                    return

            if "white_balance_gain" in settings:
                if "red" in settings["white_balance_gain"]:
                    logger.debug(
                        f"Updating the camera white balance red gain to {settings['white_balance_gain']}"
                    )
                    self.__white_balance_gain = (
                        settings["white_balance_gain"].get(
                            "red", self.__white_balance_gain[0]
                        ),
                        self.__white_balance_gain[1],
                    )
                if "blue" in settings["white_balance_gain"]:
                    logger.debug(
                        f"Updating the camera white balance blue gain to {settings['white_balance_gain']}"
                    )
                    self.__white_balance_gain = (
                        self.__white_balance_gain[0],
                        settings["white_balance_gain"].get(
                            "blue", self.__white_balance_gain[1]
                        ),
                    )
                logger.debug(
                    f"Updating the camera white balance gain to {self.__white_balance_gain}"
                )
                try:
                    self.__camera.white_balance_gain = self.__white_balance_gain
                except TimeoutError as e:
                    logger.error(
                        "A timeout has occured when setting the white balance gain, trying again"
                    )
                    self.__camera.white_balance_gain = self.__white_balance_gain
                except ValueError as e:
                    logger.error("The requested white balance gain is not valid!")
                    self.imager_client.client.publish(
                        "status/imager",
                        '{"status":"Error: White balance gain not valid"}',
                    )
                    return

            if "white_balance" in settings:
                logger.debug(
                    f"Updating the camera white balance mode to {settings['white_balance']}"
                )
                self.__white_balance = settings.get(
                    "white_balance", self.__white_balance
                )
                logger.debug(
                    f"Updating the camera white balance mode to {self.__white_balance}"
                )
                try:
                    self.__camera.white_balance = self.__white_balance
                except TimeoutError as e:
                    logger.error(
                        "A timeout has occured when setting the white balance, trying again"
                    )
                    self.__camera.white_balance = self.__white_balance
                except ValueError as e:
                    logger.error("The requested white balance is not valid!")
                    self.imager_client.client.publish(
                        "status/imager",
                        f'{"status":"Error: White balance mode {self.__white_balance} is not valid"}',
                    )
                    return

            if "image_gain" in settings:
                if "analog" in settings["image_gain"]:
                    logger.debug(
                        f"Updating the camera image analog gain to {settings['image_gain']}"
                    )
                    self.__image_gain = (
                        settings["image_gain"].get("analog", self.__image_gain[0]),
                        self.__image_gain[1],
                    )
                if "digital" in settings["image_gain"]:
                    logger.debug(
                        f"Updating the camera image digital gain to {settings['image_gain']}"
                    )
                    self.__image_gain = (
                        self.__image_gain[0],
                        settings["image_gain"].get("digital", self.__image_gain[1]),
                    )
                logger.debug(f"Updating the camera image gain to {self.__image_gain}")
                try:
                    self.__camera.image_gain = self.__image_gain
                except TimeoutError as e:
                    logger.error(
                        "A timeout has occured when setting the white balance gain, trying again"
                    )
                    self.__camera.image_gain = self.__image_gain
                except ValueError as e:
                    logger.error("The requested image gain is not valid!")
                    self.imager_client.client.publish(
                        "status/imager",
                        '{"status":"Error: Image gain not valid"}',
                    )
                    return
            # Publish the status "Config updated" to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/imager", '{"status":"Camera settings updated"}'
            )
            logger.info("Camera settings have been updated")
        else:
            logger.error("We can't update the camera settings while we are imaging.")
            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.imager_client.client.publish("status/imager", '{"status":"Busy"}')

    @logger.catch
    def treat_message(self):
        action = ""
        logger.info("We received a new message")
        if self.imager_client.msg["topic"].startswith("imager/"):
            last_message = self.imager_client.msg["payload"]
            logger.debug(last_message)
            action = self.imager_client.msg["payload"]["action"]
            logger.debug(action)
        elif self.imager_client.msg["topic"] == "status/pump":
            logger.debug(
                f"Status message payload is {self.imager_client.msg['payload']}"
            )
            if self.__imager.state.name == "waiting":
                if self.imager_client.msg["payload"]["status"] == "Done":
                    self.__imager.change(planktoscope.imager.state_machine.Capture)
                    self.imager_client.client.unsubscribe("status/pump")
                else:
                    logger.info(
                        f"The pump is not done yet {self.imager_client.msg['payload']}"
                    )
            else:
                logger.error(
                    "There is an error, we received an unexpected pump message"
                )
        else:
            logger.error(
                f"The received message was not for us! Topic was {self.imager_client.msg['topic']}"
            )
        self.imager_client.read_message()

        # If the command is "image"
        if action == "image":
            # {"action":"image","sleep":5,"volume":1,"nb_frame":200}
            self.__message_image(last_message)

        elif action == "stop":
            self.__message_stop()

        elif action == "update_config":
            self.__message_update(last_message)

        elif action == "settings":
            self.__message_settings(last_message)

        elif action not in ["image", "stop", "update_config", "settings", ""]:
            logger.warning(
                f"We did not understand the received request {action} - {last_message}"
            )

    def __pump_message(self):
        """Sends a message to the pump process"""

        planktoscope.light.pumping()

        # Pump during a given volume
        self.imager_client.client.publish(
            "actuator/pump",
            json.dumps(
                {
                    "action": "move",
                    "direction": self.__pump_direction,
                    "volume": self.__pump_volume,
                    "flowrate": 2,
                }
            ),
        )

    def __state_imaging(self):
        # subscribe to status/pump
        self.imager_client.client.subscribe("status/pump")

        # Definition of the few important metadata
        local_metadata = {
            "acq_local_datetime": datetime.datetime.now().isoformat().split(".")[0],
            "acq_camera_resolution": f"{self.__resolution[0]}x{self.__resolution[1]}",
            "acq_camera_iso": self.__iso,
            "acq_camera_shutter_speed": self.__shutter_speed,
            "acq_uuid": planktoscope.uuidName.uuidMachine(
                machine=planktoscope.uuidName.getSerial()
            ),
            "sample_uuid": planktoscope.uuidName.uuidMachine(
                machine=planktoscope.uuidName.getSerial()
            ),
        }

        # Concat the local metadata and the metadata from Node-RED
        self.__global_metadata = {**self.__global_metadata, **local_metadata}

        if "object_date" not in self.__global_metadata:
            # If this path exists, then ids are reused when they should not
            logger.error("The metadata did not contain object_date!")
            self.imager_client.client.publish(
                "status/imager",
                '{"status":"Configuration update error: object_date is missing!"}',
            )
            # Reset the counter to 0
            self.__img_done = 0
            # Change state towards stop
            self.__imager.change(planktoscope.imager.state_machine.Stop)
            planktoscope.light.error()
            return

        logger.info("Setting up the directory structure for storing the pictures")
        self.__export_path = os.path.join(
            self.__base_path,
            self.__global_metadata["object_date"],
            str(self.__global_metadata["sample_id"]).replace(" ", "_").strip("'"),
            str(self.__global_metadata["acq_id"]).replace(" ", "_").strip("'"),
        )

        if os.path.exists(self.__export_path):
            # If this path exists, then ids are reused when they should not
            logger.error(f"The export path at {self.__export_path} already exists")
            self.imager_client.client.publish(
                "status/imager",
                '{"status":"Configuration update error: Chosen id are already in use!"}',
            )
            # Reset the counter to 0
            self.__img_done = 0
            self.__imager.change(planktoscope.imager.state_machine.Stop)
            planktoscope.light.error()
            return
        else:
            # create the path!
            os.makedirs(self.__export_path)

        # Export the metadata to a json file
        logger.info("Exporting the metadata to a metadata.json")
        metadata_filepath = os.path.join(self.__export_path, "metadata.json")
        with open(metadata_filepath, "w") as metadata_file:
            json.dump(self.__global_metadata, metadata_file, indent=4)
            logger.debug(
                f"Metadata dumped in {metadata_file} are {self.__global_metadata}"
            )

        # Create the integrity file in this export path
        try:
            planktoscope.integrity.create_integrity_file(self.__export_path)
        except FileExistsError as e:
            logger.info(
                f"The integrity file already exists in this export path {self.__export_path}"
            )
        # Add the metadata.json file to the integrity file
        try:
            planktoscope.integrity.append_to_integrity_file(metadata_filepath)
        except FileNotFoundError as e:
            logger.error(
                f"{metadata_filepath} was not found, the metadata.json may not have been created properly!"
            )

        self.__pump_message()

        self.__imager.change(planktoscope.imager.state_machine.Waiting)

    def __state_capture(self):
        planktoscope.light.imaging()

        filename = f"{datetime.datetime.now().strftime('%H_%M_%S_%f')}.jpg"

        # Define the filename of the image
        filename_path = os.path.join(self.__export_path, filename)

        logger.info(
            f"Capturing image {self.__img_done + 1}/{self.__img_goal} to {filename_path}"
        )

        # Sleep a duration before to start acquisition
        time.sleep(self.__sleep_before)

        # Capture an image to the temporary file
        try:
            self.__camera.capture("", timeout=5)
        except TimeoutError as e:
            self.__capture_error("timeout during capture")
            return

        logger.debug(f"Copying the image from the temp file to {filename_path}")
        shutil.copy("/dev/shm/mjpeg/image.jpg", filename_path)  # nosec
        # TODO Try to stop the camera streaming and display instead each captured image
        # os.rename("/dev/shm/mjpeg/image.jpg", "/dev/shm/mjpeg/cam.jpg")
        logger.debug("Syncing the disk")
        os.sync()

        # Add the checksum of the captured image to the integrity file
        try:
            planktoscope.integrity.append_to_integrity_file(filename_path)
        except FileNotFoundError as e:
            self.__capture_error(f"{filename_path} was not found")
            return

        self.imager_client.client.publish(
            "status/imager",
            f'{{"status":"Image {self.__img_done + 1}/{self.__img_goal} has been imaged to {filename}"}}',
        )

        # Increment the counter
        self.__img_done += 1
        self.__error = 0

        # If counter reach the number of frame, break
        if self.__img_done >= self.__img_goal:
            self.__img_done = 0

            self.imager_client.client.publish("status/imager", '{"status":"Done"}')

            self.__imager.change(planktoscope.imager.state_machine.Stop)
            planktoscope.light.ready()
        else:
            # We have not reached the final stage, let's keep imaging
            self.imager_client.client.subscribe("status/pump")

            self.__pump_message()

            self.__imager.change(planktoscope.imager.state_machine.Waiting)

    def __capture_error(self, message=""):
        logger.error(f"An error occurred during the capture: {message}")
        planktoscope.light.error()
        if self.__error:
            logger.error("This is a repeating problem, stopping the capture now")
            self.imager_client.client.publish(
                "status/imager",
                f'{{"status":"Image {self.__img_done + 1}/{self.__img_goal} WAS NOT CAPTURED! STOPPING THE PROCESS!"}}',
            )
            self.__img_done = 0
            self.__img_goal = 0
            self.__error = 0
            self.__imager.change(planktoscope.imager.state_machine.Stop)
        else:
            self.__error += 1
            self.imager_client.client.publish(
                "status/imager",
                f'{{"status":"Image {self.__img_done + 1}/{self.__img_goal} was not captured due to this error:{message}! Retrying once!"}}',
            )
        time.sleep(1)

    @logger.catch
    def state_machine(self):
        if self.__imager.state.name == "imaging":
            self.__state_imaging()
            return

        elif self.__imager.state.name == "capture":
            self.__state_capture()
            return

        elif self.__imager.state.name == ["waiting", "stop"]:
            return

    ################################################################################
    # While loop for capturing commands from Node-RED
    ################################################################################
    @logger.catch
    def run(self):
        """This is the function that needs to be started to create a thread"""
        logger.info(
            f"The imager control thread has been started in process {os.getpid()}"
        )
        # MQTT Service connection
        self.imager_client = planktoscope.mqtt.MQTT_Client(
            topic="imager/#", name="imager_client"
        )

        self.imager_client.client.publish("status/imager", '{"status":"Starting up"}')

        if self.__camera.sensor_name == "IMX219":  # Camera v2.1
            self.imager_client.client.publish(
                "status/imager", '{"camera_name":"Camera v2.1"}'
            )
        elif self.__camera.sensor_name == "IMX477":  # Camera HQ
            self.imager_client.client.publish(
                "status/imager", '{"camera_name":"HQ Camera"}'
            )
        else:
            self.imager_client.client.publish(
                "status/imager", '{"camera_name":"Not recognized"}'
            )

        logger.info("Starting the streaming server thread")
        address = ("", 8000)
        fps = 15
        refresh_delay = 1 / fps
        handler = functools.partial(
            planktoscope.imager.streamer.StreamingHandler, refresh_delay
        )
        server = planktoscope.imager.streamer.StreamingServer(address, handler)
        self.streaming_thread = threading.Thread(
            target=server.serve_forever, daemon=True
        )
        self.streaming_thread.start()

        # Publish the status "Ready" to via MQTT to Node-RED
        self.imager_client.client.publish("status/imager", '{"status":"Ready"}')

        logger.success("Camera is READY!")

        # This is the main loop
        while not self.stop_event.is_set():
            if self.imager_client.new_message_received():
                self.treat_message()
            self.state_machine()
            time.sleep(0.001)

        logger.info("Shutting down the imager process")
        self.imager_client.client.publish("status/imager", '{"status":"Dead"}')
        logger.debug("Stopping the raspimjpeg process")
        self.__camera.close()
        logger.debug("Stopping the streaming thread")
        server.shutdown()
        logger.debug("Stopping MQTT")
        self.imager_client.shutdown()
        # self.streaming_thread.kill()
        logger.success("Imager process shut down! See you!")


# TODO This should be a test suite for this library
if __name__ == "__main__":
    pass
