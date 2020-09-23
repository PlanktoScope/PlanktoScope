# Basic planktoscope libraries
import planktoscope.mqtt
import planktoscope.light
import planktoscope.streamer
import planktoscope.imager_state_machine


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

################################################################################
# Morphocut Libraries
################################################################################
import morphocut
import morphocut.file
import morphocut.image
import morphocut.stat
import morphocut.stream
import morphocut.str
import morphocut.contrib.ecotaxa
import morphocut.contrib.zooprocess

################################################################################
# Other image processing Libraries
################################################################################
import skimage.util
import cv2


logger.info("planktoscope.imager is loaded")

################################################################################
# Main Imager class
################################################################################
class ImagerProcess(multiprocessing.Process):
    """This class contains the main definitions for the imager of the PlanktoScope"""

    def __init__(self, event, resolution=(3280, 2464), iso=60, shutter_speed=500):
        """Initialize the Imager class

        Args:
            event (multiprocessing.Event): shutdown event
            resolution (tuple, optional): Camera native resolution. Defaults to (3280, 2464).
            iso (int, optional): ISO sensitivity. Defaults to 60.
            shutter_speed (int, optional): Shutter speed of the camera. Defaults to 500.
        """
        super(ImagerProcess, self).__init__()

        logger.info("planktoscope.imager is initialising")

        self.stop_event = event
        self.__pipe = None
        self.__imager = planktoscope.imager_state_machine.Imager()
        self.__img_goal = 0
        self.__img_done = 0
        self.__sleep_before = None
        self.__pump_volume = None
        self.__img_goal = None
        self.__segmentation = None

        # PiCamera settings
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.iso = iso
        self.camera.shutter_speed = shutter_speed
        self.camera.exposure_mode = "fixedfps"

        # load config.json
        with open("/home/pi/PlanktonScope/config.json", "r") as config_file:
            node_red_metadata = json.load(config_file)
            logger.debug(f"Configuration loaded is {node_red_metadata}")

        # TODO implement a way to receive directly the metadata from Node-Red via MQTT

        # Definition of the few important metadata
        local_metadata = {
            "process_datetime": datetime.datetime.now(),
            "acq_camera_resolution": self.camera.resolution,
            "acq_camera_iso": self.camera.iso,
            "acq_camera_shutter_speed": self.camera.shutter_speed,
        }

        # Concat the local metadata and the metadata from Node-RED
        self.global_metadata = {**local_metadata, **node_red_metadata}

        # Define the name of the .zip file that will contain the images and the .tsv table for EcoTaxa
        self.archive_fn = os.path.join(
            "/home/pi/PlanktonScope/",
            "export",
            # filename includes project name, timestamp and sample id
            f"ecotaxa_export_{self.global_metadata['sample_project']}_{self.global_metadata['process_datetime']}_{self.global_metadata['sample_id']}.zip",
        )

        # Instantiate the morphocut pipeline
        self.__create_morphocut_pipeline()

        logger.info("planktoscope.imager is initialised and ready to go!")

    def __create_morphocut_pipeline(self):
        """Creates the Morphocut Pipeline"""
        logger.debug("Let's start creating the Morphocut Pipeline")

        with morphocut.Pipeline() as self.__pipe:
            # TODO wrap morphocut.Call(logger.debug()) in something that allows it not to be added to the pipeline
            # if the logger.level is not debug. Might not be as easy as it sounds.
            # Recursively find .jpg files in import_path.
            # Sort to get consective frames.
            abs_path = morphocut.file.Find(
                "/home/pi/PlanktonScope/tmp", [".jpg"], sort=True, verbose=True
            )

            # Extract name from abs_path
            name = morphocut.Call(
                lambda p: os.path.splitext(os.path.basename(p))[0], abs_path
            )

            # Set the LEDs as Green
            morphocut.Call(planktoscope.light.setRGB, 0, 255, 0)

            # Read image
            img = morphocut.image.ImageReader(abs_path)

            # Show progress bar for frames
            morphocut.stream.TQDM(morphocut.str.Format("Frame {name}", name=name))

            # Apply running median to approximate the background image
            flat_field = morphocut.stat.RunningMedian(img, 5)

            # Correct image
            img = img / flat_field

            # Rescale intensities and convert to uint8 to speed up calculations
            img = morphocut.image.RescaleIntensity(
                img, in_range=(0, 1.1), dtype="uint8"
            )

            # Filter variable to reduce memory load
            morphocut.stream.FilterVariables(name, img)

            # Save cleaned images
            # frame_fn = morphocut.str.Format(os.path.join("/home/pi/PlanktonScope/tmp","CLEAN", "{name}.jpg"), name=name)
            # morphocut.image.ImageWriter(frame_fn, img)

            # Convert image to uint8 gray
            img_gray = morphocut.image.RGB2Gray(img)

            # ?
            img_gray = morphocut.Call(skimage.util.img_as_ubyte, img_gray)

            # Canny edge detection using OpenCV
            img_canny = morphocut.Call(cv2.Canny, img_gray, 50, 100)

            # Dilate using OpenCV
            kernel = morphocut.Call(
                cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (15, 15)
            )
            img_dilate = morphocut.Call(cv2.dilate, img_canny, kernel, iterations=2)

            # Close using OpenCV
            kernel = morphocut.Call(
                cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (5, 5)
            )
            img_close = morphocut.Call(
                cv2.morphologyEx, img_dilate, cv2.MORPH_CLOSE, kernel, iterations=1
            )

            # Erode using OpenCV
            kernel = morphocut.Call(
                cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (15, 15)
            )
            mask = morphocut.Call(cv2.erode, img_close, kernel, iterations=2)

            # Find objects
            regionprops = morphocut.image.FindRegions(
                mask, img_gray, min_area=1000, padding=10, warn_empty=name
            )

            # Set the LEDs as Purple
            morphocut.Call(planktoscope.light.setRGB, 255, 0, 255)

            # For an object, extract a vignette/ROI from the image
            roi_orig = morphocut.image.ExtractROI(img, regionprops, bg_color=255)

            # Generate an object identifier
            i = morphocut.stream.Enumerate()

            # morphocut.Call(print,i)

            # Define the ID of each object
            object_id = morphocut.str.Format("{name}_{i:d}", name=name, i=i)

            # morphocut.Call(print,object_id)

            # Define the name of each object
            object_fn = morphocut.str.Format(
                os.path.join("/home/pi/PlanktonScope/", "OBJECTS", "{name}.jpg"),
                name=object_id,
            )

            # Save the image of the object with its name
            morphocut.image.ImageWriter(object_fn, roi_orig)

            # Calculate features. The calculated features are added to the global_metadata.
            # Returns a Variable representing a dict for every object in the stream.
            meta = morphocut.contrib.zooprocess.CalculateZooProcessFeatures(
                regionprops, prefix="object_", meta=self.global_metadata
            )

            # Get all the metadata
            json_meta = morphocut.Call(json.dumps, meta, sort_keys=True, default=str)

            # Publish the json containing all the metadata to via MQTT to Node-RED
            morphocut.Call(
                self.imager_client.client.publish,
                "status/segmentation/metric",
                json_meta,
            )

            # Add object_id to the metadata dictionary
            meta["object_id"] = object_id

            # Generate object filenames
            orig_fn = morphocut.str.Format("{object_id}.jpg", object_id=object_id)

            # Write objects to an EcoTaxa archive:
            # roi image in original color, roi image in grayscale, metadata associated with each object
            morphocut.contrib.ecotaxa.EcotaxaWriter(
                self.archive_fn, (orig_fn, roi_orig), meta
            )

            # Progress bar for objects
            morphocut.stream.TQDM(
                morphocut.str.Format("Object {object_id}", object_id=object_id)
            )

            # Publish the object_id to via MQTT to Node-RED
            morphocut.Call(
                self.imager_client.client.publish,
                "status/segmentation/object_id",
                f'{{"object_id":"{object_id}"}}',
            )

            # Set the LEDs as Green
            morphocut.Call(planktoscope.light.setRGB, 0, 255, 0)
        logger.info("Morphocut's Pipeline has been created")

    def start_camera(self, output):
        """Start the camera streaming process

        Args:
            output (planktoscope.streamer.StreamingOutput(), required): Streaming output
                            of the created server
        """
        self.camera.start_recording(output, format="mjpeg", resize=(640, 480))

    def pump_callback(self, client, userdata, msg):
        # Print the topic and the message
        logger.info(f"{self.name}: {msg.topic} {str(msg.qos)} {str(msg.payload)}")
        if msg.topic != "status/pump":
            logger.error(
                f"The received message has the wrong topic {msg.topic}, payload was {str(msg.payload)}"
            )
            return
        payload = json.loads(msg.payload.decode())
        logger.debug(f"parsed payload is {self.payload}")
        if self.__imager.state.name is "waiting":
            if payload["status"] is "Done":
                self.__imager.change(planktoscope.imager_state_machine.Capture)
                self.imager_client.client.message_callback_remove("status/pump")
                self.imager_client.client.unsubscribe("status/pump")
            else:
                logger.info(f"the pump is not done yet {payload}")
        else:
            logger.error(
                "There is an error, status is not waiting for the pump and yet we received a pump message"
            )

    def treat_message(self):
        action = ""
        if self.imager_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.imager_client.msg["payload"]
            logger.debug(last_message)
            action = self.imager_client.msg["payload"]["action"]
            logger.debug(command)
            self.imager_client.read_message()

        # If the command is "image"
        if action == "image":
            # {"action":"image","sleep":5,"volume":1,"nb_frame":200, "segmentation":False}
            if (
                "sleep" not in last_message
                or "volume" not in last_message
                or "nb_frame" not in last_message
                or "segmentation" not in last_message
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
            # Get the segmentation status (true/false) from the different received arguments
            self.__segmentation = bool(last_message["segmentation"])

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
                logger.info("Updating the configuration now with the received data")
                # Updating the configuration with the passed parameter in payload["config"]

                # Publish the status "Interrupted" to via MQTT to Node-RED
                self.imager_client.client.publish(
                    "status/imager", '{"status":"Config updated"}'
                )
            else:
                logger.error("We can't update the configuration while we are imaging.")
                # Publish the status "Interrupted" to via MQTT to Node-RED
                self.imager_client.client.publish("status/imager", '{"status":"Busy"}')
            pass

        elif action != "":
            logger.warning(
                f"We did not understand the received request {action} - {last_message}"
            )

    def state_machine(self):
        if self.__imager.state.name is "imaging":
            # subscribe to status/pump
            self.imager_client.client.subscribe("status/pump")
            self.imager_client.client.message_callback_add(
                "status/pump", self.pump_callback
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
                        "direction": "BACKWARD",
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

            # Print datetime
            logger.info("Capturing an image")

            # Define the filename of the image
            filename = os.path.join(
                "/home/pi/PlanktonScope/tmp",
                datetime.now().strftime("%H_%M_%S_%f") + ".jpg",
            )

            # Capture an image with the proper filename
            self.camera.capture(filename)

            # Set the LEDs as Green
            planktoscope.light.setRGB(0, 255, 0)

            # Publish the name of the image to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/imager",
                f'{{"status":"{datetime_tmp} .jpg has been imaged."}}',
            )

            # Increment the counter
            self.__img_done += 1

            # If counter reach the number of frame, break
            if self.__img_done >= self.__img_goal:
                # Reset the counter to 0
                self.__img_done = 0

                # Publish the status "Done" to via MQTT to Node-RED
                self.imager_client.client.publish("status/imager", '{"status":"Done"}')

                if self.__segmentation:
                    # Change state towards Segmentation
                    self.__imager.change(planktoscope.imager_state_machine.Segmentation)
                else:
                    # Change state towards done
                    self.__imager.change(planktoscope.imager_state_machine.Stop)
                    # Set the LEDs as Green
                    planktoscope.light.setRGB(0, 255, 255)

                return
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

        elif self.__imager.state.name is "segmentation":
            # Publish the status "Started" to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/segmentation", '{"status":"Started"}'
            )

            # Start the MorphoCut Pipeline
            self.__pipe.run()

            # remove directory
            # shutil.rmtree(import_path)

            # Publish the status "Done" to via MQTT to Node-RED
            self.imager_client.client.publish(
                "status/segmentation", '{"status":"Done"}'
            )

            # Set the LEDs as White
            planktoscope.light.setRGB(255, 255, 255)

            # cmd = os.popen("rm -rf /home/pi/PlanktonScope/tmp/*.jpg")

            # Set the LEDs as Green
            planktoscope.light.setRGB(0, 255, 0)
            # Change state towards Waiting for pump
            self.__imager.change(planktoscope.imager_state_machine.Stop)
            return

        elif self.__imager.state.name is "waiting":
            return

        elif self.__imager.state.name is "stop":
            return

    ################################################################################
    # While loop for capturing commands from Node-RED
    ################################################################################
    @logger.catch
    def run(self):
        """This is the function that needs to be started to create a thread

        This function runs for perpetuity. For now, it has no exit methods
        (hence no cleanup is performed on exit/kill). However, atexit can
        probably be used for this. See https://docs.python.org/3.8/library/atexit.html
        Eventually, the __del__ method could be used, if this module is
        made into a class.
        """
        # MQTT Service connection
        self.imager_client = planktoscope.mqtt.MQTT_Client(
            topic="imager/#", name="imager_client"
        )

        while not self.stop_event.is_set():
            self.treat_message()
            self.state_machine()

        logger.info("Shutting down the imager process")
        self.imager_client.client.publish("status/imager", '{"status":"Dead"}')
        self.imager_client.shutdown()
