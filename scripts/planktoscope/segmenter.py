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

# Library for starting processes
import multiprocessing

# Basic planktoscope libraries
import planktoscope.mqtt
import planktoscope.light


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

logger.info("planktoscope.segmenter is loaded")


################################################################################
# Main Segmenter class
################################################################################
class SegmenterProcess(multiprocessing.Process):
    """This class contains the main definitions for the segmenter of the PlanktoScope"""

    @logger.catch
    def __init__(self, event):
        """Initialize the Segmenter class

        Args:
            event (multiprocessing.Event): shutdown event
        """
        super(SegmenterProcess, self).__init__(name="segmenter")

        logger.info("planktoscope.segmenter is initialising")

        self.stop_event = event
        self.__pipe = None
        self.segmenter_client = None
        self.__img_path = "/home/pi/PlanktonScope/img"
        self.__export_path = "/home/pi/PlanktonScope/export"
        self.__ecotaxa_path = os.path.join(self.__export_path, "ecotaxa")
        self.__global_metadata = None
        self.__working_path = ""

        if not os.path.exists(self.__ecotaxa_path):
            # create the path!
            os.makedirs(self.__ecotaxa_path)
        # Morphocut's pipeline will be created at runtime otherwise shit ensues

        logger.info("planktoscope.segmenter is initialised and ready to go!")

    def __create_morphocut_pipeline(self):
        """Creates the Morphocut Pipeline"""
        logger.debug("Let's start creating the Morphocut Pipeline")

        with morphocut.Pipeline() as self.__pipe:
            # TODO wrap morphocut.Call(logger.debug()) in something that allows it not to be added to the pipeline
            # if the logger.level is not debug. Might not be as easy as it sounds.
            # Recursively find .jpg files in import_path.
            # Sort to get consective frames.
            abs_path = morphocut.file.Find(
                self.__working_path, [".jpg"], sort=True, verbose=True
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
                regionprops, prefix="object_", meta=self.__global_metadata
            )

            # Get all the metadata
            json_meta = morphocut.Call(json.dumps, meta, sort_keys=True, default=str)

            # Publish the json containing all the metadata to via MQTT to Node-RED
            morphocut.Call(
                self.segmenter_client.client.publish,
                "status/segmentater/metric",
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
                self.segmenter_client.client.publish,
                "status/segmentater/object_id",
                f'{{"object_id":"{object_id}"}}',
            )

            # Set the LEDs as Green
            morphocut.Call(planktoscope.light.setRGB, 0, 255, 0)
        logger.info("Morphocut's Pipeline has been created")

    @logger.catch
    def treat_message(self):
        action = ""
        if self.segmenter_client.new_message_received():
            logger.info("We received a new message")
            last_message = self.segmenter_client.msg["payload"]
            logger.debug(last_message)
            action = self.segmenter_client.msg["payload"]["action"]
            self.segmenter_client.read_message()

        # If the command is "segment"
        if action == "segment":
            # {"action":"segment"}
            # Publish the status "Started" to via MQTT to Node-RED
            self.segmenter_client.client.publish(
                "status/segmenter", '{"status":"Started"}'
            )

            img_paths = [x[0] for x in os.walk(self.__img_path)]
            logger.info(f"The pipeline will be run in {len(img_paths)} directories")
            for path in img_paths:
                logger.info(f"Loading the metadata file for {path}")
                with open(os.path.join(path, "metadata.json"), "r") as config_file:
                    self.__global_metadata = json.load(config_file)
                    logger.debug(f"Configuration loaded is {self.__global_metadata}")

                # Define the name of the .zip file that will contain the images and the .tsv table for EcoTaxa
                self.archive_fn = os.path.join(
                    self.__ecotaxa_path,
                    # filename includes project name, timestamp and sample id
                    f"export_{self.__global_metadata['sample_project']}_{self.__global_metadata['process_datetime']}_{self.__global_metadata['sample_id']}.zip",
                )

                logger.info(f"Starting the pipeline in {path}")
                # Start the MorphoCut Pipeline on the found path
                self.__working_path = path

                @logger.catch
                self.__pipe.run()
                logger.info(f"Pipeline has been run for {path}")

            # remove directory
            # shutil.rmtree(import_path)

            # Publish the status "Done" to via MQTT to Node-RED
            self.segmenter_client.client.publish(
                "status/segmenter", '{"status":"Done"}'
            )

            # Set the LEDs as White
            planktoscope.light.setRGB(255, 255, 255)

            # cmd = os.popen("rm -rf /home/pi/PlanktonScope/tmp/*.jpg")

            # Set the LEDs as Green
            planktoscope.light.setRGB(0, 255, 0)

        elif action == "stop":
            logger.info("The segmentation has been interrupted.")

            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.segmenter_client.client.publish(
                "status/segmenter", '{"status":"Interrupted"}'
            )

        elif action == "update_config":
            logger.error("We can't update the configuration while we are segmenting.")
            # Publish the status "Interrupted" to via MQTT to Node-RED
            self.segmenter_client.client.publish(
                "status/segmenter", '{"status":"Busy"}'
            )
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
            f"The segmenter control thread has been started in process {os.getpid()}"
        )
        # MQTT Service connection
        self.segmenter_client = planktoscope.mqtt.MQTT_Client(
            topic="segmenter/#", name="segmenter_client"
        )

        # Instantiate the morphocut pipeline
        self.__create_morphocut_pipeline()

        # Publish the status "Ready" to via MQTT to Node-RED
        self.segmenter_client.client.publish("status/segmenter", '{"status":"Ready"}')

        logger.info("Ready to roll!")

        # This is the loop
        while not self.stop_event.is_set():
            self.treat_message()
            time.sleep(0.5)

        logger.info("Shutting down the segmenter process")
        self.segmenter_client.client.publish("status/segmenter", '{"status":"Dead"}')
        self.segmenter_client.shutdown()
        logger.info("Segmenter process shut down! See you!")
