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
import json, shutil

# Library for path and filesystem manipulations
import os

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import planktoscope.mqtt
import planktoscope.light

# import planktoscope.streamer
import planktoscope.imager_state_machine

# import raspimjpeg module
import planktoscope.raspimjpeg

# Integrity verification module
import planktoscope.integrity

# Uuid module
import planktoscope.uuidName


################################################################################
# Streaming PiCamera over server
################################################################################
import socketserver
import http.server
import threading
import functools


################################################################################
# Classes for the PiCamera Streaming
################################################################################
class StreamingHandler(http.server.BaseHTTPRequestHandler):
    # Webpage content containing the PiCamera Streaming
    PAGE = """\
    <html>
    <head>
    <title>PlanktonScope v2 | PiCamera Streaming</title>
    </head>
    <body>
    <img src="stream.mjpg" width="100%" height="100%" />
    </body>
    </html>
    """

    def __init__(self, delay, *args, **kwargs):
        self.delay = delay
        super(StreamingHandler, self).__init__(*args, **kwargs)

    @logger.catch
    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            content = self.PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", 0)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
            )

            self.end_headers()
            try:
                while True:
                    try:
                        with open("/dev/shm/mjpeg/cam.jpg", "rb") as jpeg:
                            frame = jpeg.read()
                    except FileNotFoundError as e:
                        logger.error(f"Camera has not been started yet")
                        time.sleep(5)
                    except Exception as e:
                        logger.exception(f"An exception occured {e}")
                    else:
                        self.wfile.write(b"--FRAME\r\n")
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
                        time.sleep(self.delay)

            except BrokenPipeError as e:
                logger.info(f"Removed streaming client {self.client_address}")
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


logger.info("planktoscope.imager is loaded")

################################################################################
# Main Imager class
################################################################################
class ImagerProcess(multiprocessing.Process):
    """This class contains the main definitions for the imager of the PlanktoScope"""

    @logger.catch
    def __init__(self, stop_event, iso=100, shutter_speed=1):
        """Initialize the Imager class

        Args:
            stop_event (multiprocessing.Event): shutdown event
            iso (int, optional): ISO sensitivity. Defaults to 100.
            shutter_speed (int, optional): Shutter speed of the camera. Defaults to 500.
        """
        super(ImagerProcess, self).__init__(name="imager")

        logger.info("planktoscope.imager is initialising")

        if os.path.exists("/home/pi/PlanktonScope/hardware.json"):
            # load hardware.json
            with open("/home/pi/PlanktonScope/hardware.json", "r") as config_file:
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
        self.__imager = planktoscope.imager_state_machine.Imager()
        self.__img_goal = 0
        self.__img_done = 0
        self.__sleep_before = None
        self.__pump_volume = None
        self.__pump_direction = "FORWARD"
        self.__img_goal = None
        self.imager_client = None

        # Initialise the camera and the process
        # Also starts the streaming to the temporary file
        self.__camera = planktoscope.raspimjpeg.raspimjpeg()

        try:
            self.__camera.start()
        except Exception as e:
            logger.exception(
                f"An exception has occured when starting up raspimjpeg: {e}"
            )
            exit(1)

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
        self.__exposure_mode = "fixedfps"
        self.__white_balance = "off"
        self.__white_balance_gain = (
            configuration.get("wb_red_gain", 2.00) * 100,
            configuration.get("wb_blue_gain", 1.40) * 100,
        )  # Those values were tested on a HQ camera to give a whitish background

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
        self.__imager.change(planktoscope.imager_state_machine.Imaging)

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

        self.__imager.change(planktoscope.imager_state_machine.Stop)

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
                    self.__imager.change(planktoscope.imager_state_machine.Capture)
                    self.imager_client.client.unsubscribe("status/pump")
                else:
                    logger.info(f"The pump is not done yet {payload}")
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
            "acq_camera_resolution": self.__resolution,
            "acq_camera_iso": self.__iso,
            "acq_camera_shutter_speed": self.__shutter_speed,
            "acq_uuid": planktoscope.uuidName.uuidMachineName(
                machine=planktoscope.uuidName.getSerial()
            ),
            "sample_uuid": planktoscope.uuidName.uuidMachineName(
                machine=planktoscope.uuidName.getSerial()
            ),
        }

        # Concat the local metadata and the metadata from Node-RED
        self.__global_metadata = {**self.__global_metadata, **local_metadata}

        if "object_date" not in self.__global_metadata:
            # If this path exists, then ids are reused when they should not
            logger.error(f"The metadata did not contain object_date!")
            self.imager_client.client.publish(
                "status/imager",
                '{"status":"Configuration update error: object_date is missing!"}',
            )
            # Reset the counter to 0
            self.__img_done = 0
            # Change state towards stop
            self.__imager.change(planktoscope.imager_state_machine.Stop)
            planktoscope.light.error()
            return

        logger.info("Setting up the directory structure for storing the pictures")
        self.__export_path = os.path.join(
            self.__base_path,
            self.__global_metadata["object_date"],
            str(self.__global_metadata["sample_id"]).replace(" ", "_"),
            str(self.__global_metadata["acq_id"]).replace(" ", "_"),
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
            self.__imager.change(planktoscope.imager_state_machine.Stop)
            planktoscope.light.error()
            return
        else:
            # create the path!
            os.makedirs(self.__export_path)

        # Export the metadata to a json file
        logger.info("Exporting the metadata to a metadata.json")
        metadata_filepath = os.path.join(self.__export_path, "metadata.json")
        with open(metadata_filepath, "w") as metadata_file:
            json.dump(self.__global_metadata, metadata_file)
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

        self.__imager.change(planktoscope.imager_state_machine.Waiting)

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

        # Capture an image with the proper filename
        try:
            self.__camera.capture(filename_path)
        except TimeoutError as e:
            logger.error("A timeout happened while waiting for a capture to happen")
            # Publish the name of the image to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/imager",
                f'{{"status":"Image {self.__img_done + 1}/{self.__img_goal} WAS NOT CAPTURED! STOPPING THE PROCESS!"}}',
            )
            # Reset the counter to 0
            self.__img_done = 0
            self.__img_goal = 0
            self.__imager.change(planktoscope.imager_state_machine.Stop)
            planktoscope.light.error()
            return

        # Add the checksum of the captured image to the integrity file
        try:
            planktoscope.integrity.append_to_integrity_file(filename_path)
        except FileNotFoundError as e:
            logger.error(
                f"{filename_path} was not found, the camera did not work properly! Trying again"
            )
            self.imager_client.client.publish(
                "status/imager",
                f'{{"status":"Image {self.__img_done + 1}/{self.__img_goal} was not found, retrying the capture now."}}',
            )
            # Let's try again after a tiny delay!
            time.sleep(1)
            return

        # Publish the name of the image to via MQTT to Node-RED
        self.imager_client.client.publish(
            "status/imager",
            f'{{"status":"Image {self.__img_done + 1}/{self.__img_goal} has been imaged to {filename}"}}',
        )

        # Increment the counter
        self.__img_done += 1

        # If counter reach the number of frame, break
        if self.__img_done >= self.__img_goal:
            self.__img_done = 0

            self.imager_client.client.publish("status/imager", '{"status":"Done"}')

            self.__imager.change(planktoscope.imager_state_machine.Stop)
            planktoscope.light.ready()
            return
        else:
            # We have not reached the final stage, let's keep imaging
            self.imager_client.client.subscribe("status/pump")

            self.__pump_message()

            self.__imager.change(planktoscope.imager_state_machine.Waiting)

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
        fps = 16
        refresh_delay = 1 / fps
        handler = functools.partial(StreamingHandler, refresh_delay)
        server = StreamingServer(address, handler)
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


# This is called if this script is launched directly
if __name__ == "__main__":
    # TODO This should be a test suite for this library
    pass