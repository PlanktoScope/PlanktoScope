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
import json, shutil, os

# Library to control the PiCamera
import picamera

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import planktoscope.mqtt
import planktoscope.light

# import planktoscope.streamer
import planktoscope.imager_state_machine


################################################################################
# Streaming PiCamera over server
################################################################################
import io
import socketserver
import http.server
import threading

################################################################################
# Classes for the PiCamera Streaming
################################################################################
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


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
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    # TODO exception BrokenPipeError here
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                logger.exception(f"Removed streaming client {self.client_address}")
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


output = StreamingOutput()

logger.info("planktoscope.imager is loaded")


################################################################################
# Main Imager class
################################################################################
class ImagerProcess(multiprocessing.Process):
    """This class contains the main definitions for the imager of the PlanktoScope"""

    @logger.catch
    def __init__(self, event, resolution=(3280, 2464), iso=60, shutter_speed=500):
        """Initialize the Imager class

        Args:
            event (multiprocessing.Event): shutdown event
            resolution (tuple, optional): Camera native resolution. Defaults to (3280, 2464).
            iso (int, optional): ISO sensitivity. Defaults to 60.
            shutter_speed (int, optional): Shutter speed of the camera. Defaults to 500.
        """
        super(ImagerProcess, self).__init__(name="imager")

        logger.info("planktoscope.imager is initialising")

        self.stop_event = event
        self.__imager = planktoscope.imager_state_machine.Imager()
        self.__img_goal = 0
        self.__img_done = 0
        self.__sleep_before = None
        self.__pump_volume = None
        self.__img_goal = None
        self.imager_client = None
        self.__camera = None
        self.__resolution = resolution
        self.__iso = iso
        self.__shutter_speed = shutter_speed
        self.__exposure_mode = "fixedfps"
        self.__base_path = "/home/pi/data/img"
        self.__export_path = ""
        self.__global_metadata = None

        logger.success("planktoscope.imager is initialised and ready to go!")

    @logger.catch
    def start_camera(self):
        """Start the camera streaming process"""
        self.__camera.start_recording(output, format="mjpeg", resize=(640, 480))

    def pump_callback(self, client, userdata, msg):
        # Print the topic and the message
        logger.info(f"{self.name}: {msg.topic} {str(msg.qos)} {str(msg.payload)}")
        if msg.topic != "status/pump":
            logger.error(
                f"The received message has the wrong topic {msg.topic}, payload was {str(msg.payload)}"
            )
            return
        payload = json.loads(msg.payload.decode())
        logger.debug(f"parsed payload is {payload}")
        if self.__imager.state.name is "waiting":
            if payload["status"] == "Done":
                self.__imager.change(planktoscope.imager_state_machine.Capture)
                self.imager_client.client.message_callback_remove("status/pump")
                self.imager_client.client.unsubscribe("status/pump")
            else:
                logger.info(f"the pump is not done yet {payload}")
        else:
            logger.error(
                "There is an error, status is not waiting for the pump and yet we received a pump message"
            )

    @logger.catch
    def treat_message(self):
        action = ""
        if self.imager_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.imager_client.msg["payload"]
            logger.debug(last_message)
            action = self.imager_client.msg["payload"]["action"]
            logger.debug(action)
            self.imager_client.read_message()

        # If the command is "image"
        if action == "image":
            # {"action":"image","sleep":5,"volume":1,"nb_frame":200}
            if (
                "sleep" not in last_message
                or "volume" not in last_message
                or "nb_frame" not in last_message
            ):
                logger.error(
                    f"The received message has the wrong argument {last_message}"
                )
                self.imager_client.client.publish("status/imager", '{"status":"Error"}')
                return

            # Change the state of the machine
            self.__imager.change(planktoscope.imager_state_machine.Imaging)

            # Get duration to wait before an image from the different received arguments
            self.__sleep_before = float(last_message["sleep"])
            # Get volume in between two images from the different received arguments
            self.__pump_volume = float(last_message["volume"])
            # Get the number of frames to image from the different received arguments
            self.__img_goal = int(last_message["nb_frame"])

            self.imager_client.client.publish("status/imager", '{"status":"Started"}')

        elif action == "stop":
            # Remove callback for "status/pump" and unsubscribe
            self.imager_client.client.message_callback_remove("status/pump")
            self.imager_client.client.unsubscribe("status/pump")

            # Stops the pump
            self.imager_client.client.publish("actuator/pump", '{"action": "stop"}')

            logger.info("The imaging has been interrupted.")

            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/imager", '{"status":"Interrupted"}'
            )

            # Set the LEDs as Green
            planktoscope.light.setRGB(0, 255, 0)

            # Change state to Stop
            self.__imager.change(planktoscope.imager_state_machine.Stop)

        elif action == "update_config":
            if self.__imager.state.name is "stop":
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
                nodered_metadata = last_message["config"]
                # Definition of the few important metadata
                local_metadata = {
                    "process_datetime": datetime.datetime.now()
                    .isoformat()
                    .split(".")[0],
                    "acq_camera_resolution": self.__resolution,
                    "acq_camera_iso": self.__iso,
                    "acq_camera_shutter_speed": self.__shutter_speed,
                }
                # Concat the local metadata and the metadata from Node-RED
                self.__global_metadata = {**local_metadata, **nodered_metadata}

                # Publish the status "Config updated" to via MQTT to Node-RED
                self.imager_client.client.publish(
                    "status/imager", '{"status":"Config updated"}'
                )
                logger.info("Configuration has been updated")
            else:
                logger.error("We can't update the configuration while we are imaging.")
                # Publish the status "Interrupted" to via MQTT to Node-RED
                self.imager_client.client.publish("status/imager", '{"status":"Busy"}')
        elif action == "settings":
            if self.__imager.state.name is "stop":
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
                    logger.debug(
                        f"Updating the camera resolution to {self.__resolution}"
                    )
                    self.__camera.resolution = self.__resolution

                if "iso" in settings:
                    self.__iso = settings.get("iso", self.__iso)
                    logger.debug(f"Updating the camera iso to {self.__iso}")
                    self.__camera.iso = self.__iso

                if "shutter_speed" in settings:
                    self.__shutter_speed = settings.get(
                        "shutter_speed", self.__shutter_speed
                    )
                    logger.debug(
                        f"Updating the camera shutter speed to {self.__shutter_speed}"
                    )
                    self.__camera.shutter_speed = self.__shutter_speed

                # Publish the status "Config updated" to via MQTT to Node-RED
                self.imager_client.client.publish(
                    "status/imager", '{"status":"Camera settings updated"}'
                )
                logger.info("Camera settings have been updated")
            else:
                logger.error(
                    "We can't update the camera settings while we are imaging."
                )
                # Publish the status "Interrupted" to via MQTT to Node-RED
                self.imager_client.client.publish("status/imager", '{"status":"Busy"}')
        elif action != "":
            logger.warning(
                f"We did not understand the received request {action} - {last_message}"
            )

    @logger.catch
    def state_machine(self):
        if self.__imager.state.name is "imaging":
            # subscribe to status/pump
            self.imager_client.client.subscribe("status/pump")
            self.imager_client.client.message_callback_add(
                "status/pump", self.pump_callback
            )

            logger.info("Setting up the directory structure for storing the pictures")
            self.__export_path = os.path.join(
                self.__base_path,
                # We only keep the date '2020-09-25T15:25:21.079769'
                self.__global_metadata["process_datetime"].split("T")[0],
                str(self.__global_metadata["sample_id"]),
                str(self.__global_metadata["acq_id"]),
            )
            if not os.path.exists(self.__export_path):
                # create the path!
                os.makedirs(self.__export_path)

            # Export the metadata to a json file
            logger.info("Exporting the metadata to a metadata.json")
            config_path = os.path.join(self.__export_path, "metadata.json")
            with open(config_path, "w") as metadata_file:
                json.dump(self.__global_metadata, metadata_file)
                logger.debug(
                    f"Metadata dumped in {metadata_file} are {self.__global_metadata}"
                )

            # Sleep a duration before to start acquisition
            time.sleep(self.__sleep_before)

            # Set the LEDs as Blue
            planktoscope.light.setRGB(0, 0, 255)
            self.imager_client.client.publish(
                "actuator/pump",
                json.dumps(
                    {
                        "action": "move",
                        "direction": "FORWARD",
                        "volume": self.__pump_volume,
                        "flowrate": 2,
                    }
                ),
            )
            # FIXME We should probably update the global metadata here with the current datetime/position/etc...

            # Set the LEDs as Green
            planktoscope.light.setRGB(0, 255, 0)

            # Change state towards Waiting for pump
            self.__imager.change(planktoscope.imager_state_machine.Waiting)
            return

        elif self.__imager.state.name is "capture":
            # Set the LEDs as Cyan
            planktoscope.light.setRGB(0, 255, 255)

            filename = f"{datetime.datetime.now().strftime('%H_%M_%S_%f')}.jpg"

            # Define the filename of the image
            filename_path = os.path.join(self.__export_path, filename)

            logger.info(
                f"Capturing image {self.__img_done + 1}/{self.__img_goal} to {filename_path}"
            )

            # Capture an image with the proper filename
            self.__camera.capture(filename_path)

            # Set the LEDs as Green
            planktoscope.light.setRGB(0, 255, 0)

            # Publish the name of the image to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/imager",
                f'{{"status":"Image {self.__img_done + 1}/{self.__img_goal} has been imaged to {filename}"}}',
            )

            # Increment the counter
            self.__img_done += 1

            # If counter reach the number of frame, break
            if self.__img_done >= self.__img_goal:
                # Reset the counter to 0
                self.__img_done = 0

                # Publish the status "Done" to via MQTT to Node-RED
                self.imager_client.client.publish("status/imager", '{"status":"Done"}')

                # Change state towards done
                self.__imager.change(planktoscope.imager_state_machine.Stop)
                # Set the LEDs as Green
                planktoscope.light.setRGB(0, 255, 255)
            else:
                # We have not reached the final stage, let's keep imaging
                # Set the LEDs as Blue
                planktoscope.light.setRGB(0, 0, 255)

                # subscribe to status/pump
                self.imager_client.client.subscribe("status/pump")
                self.imager_client.client.message_callback_add(
                    "status/pump", self.pump_callback
                )

                # Pump during a given volume
                self.imager_client.client.publish(
                    "actuator/pump",
                    json.dumps(
                        {
                            "action": "move",
                            "direction": "BACKWARD",
                            "volume": self.__pump_volume,
                            "flowrate": 2,
                        }
                    ),
                )

                # Set the LEDs as Green
                planktoscope.light.setRGB(0, 255, 0)

                # Change state towards Waiting for pump
                self.__imager.change(planktoscope.imager_state_machine.Waiting)
            return
        elif (
            self.__imager.state.name is "waiting"
            or self.__imager.state.name is "stop"
        ):
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

        logger.info("Initialising the camera")
        # PiCamera settings
        self.__camera = picamera.PiCamera(resolution=self.__resolution)
        self.__camera.iso = self.__iso
        self.__camera.shutter_speed = self.__shutter_speed
        self.__camera.exposure_mode = self.__exposure_mode

        address = ("", 8000)
        server = StreamingServer(address, StreamingHandler)
        # Starts the streaming server process
        logger.info("Starting the streaming server thread")
        self.start_camera()
        self.streaming_thread = threading.Thread(
            target=server.serve_forever, daemon=True
        )
        self.streaming_thread.start()

        # Publish the status "Ready" to via MQTT to Node-RED
        self.imager_client.client.publish("status/imager", '{"status":"Ready"}')

        logger.success("Camera is READY!")

        # This is the loop
        while not self.stop_event.is_set():
            self.treat_message()
            self.state_machine()
            time.sleep(0.001)

        logger.info("Shutting down the imager process")
        self.imager_client.client.publish("status/imager", '{"status":"Dead"}')
        logger.debug("Stopping the camera")
        self.__camera.stop_recording()
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