# Basic planktoscope libraries
import planktoscope.mqtt
import planktoscope.light
import planktoscope.streamer
import multiprocessing

# Logger library compatible with multiprocessing
from loguru import logger

logger.info("planktoscope.imager is loaded")


################################################################################
# Practical Libraries
################################################################################

# Library to get date and time for folder name and filename
import datetime

# Library to be able to sleep for a given duration
import time

# Libraries manipulate json format, execute bash commands
import json, shutil, os

# Library to control the PiCamera
import picamera

################################################################################
# Morphocut Library
################################################################################
import morphocut

################################################################################
# Other image processing Libraries
################################################################################
import skimage
import cv2


################################################################################
# Main Imager class
################################################################################
class ImagerProcess(multiprocessing.Process):
    """This class contains the main definitions for the imager of the PlanktoScope"""

    def __init__(self, resolution=(3280, 2464), iso=60, shutter_speed=500, event):
        """Initialize the Imager class

        Args:
            resolution (tuple, optional): Camera native resolution. Defaults to (3280, 2464).
            iso (int, optional): ISO sensitivity. Defaults to 60.
            shutter_speed (int, optional): Shutter speed of the camera. Defaults to 500.
            event (multiprocessing.Event): shutdown event
        """
        super(ImagerProcess, self).__init__()

        logger.info("planktoscope.imager is initialized")
        
        self.stop_event = event

        # PiCamera settings
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.iso = iso
        self.camera.shutter_speed = shutter_speed
        self.camera.exposure_mode = "fixedfps"

        # MQTT Service connection
        self.imaging_client = planktoscope.mqtt.MQTT_Client(
            topic="imager/#", name="imager_client"
        )
        self.imaging_client.connect()

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
        self._create_morphocut_pipeline(self)

    def _create_morphocut_pipeline(self):
        """Creates the Morphocut Pipeline"""
        logger.debug("Let's start creating the Morphocut Pipeline")

        with morphocut.morphocut.Pipeline() as self.pipe:
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
            img_gray = morphocut.Call(img_as_ubyte, img_gray)

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
            meta = CalculateZooProcessFeatures(
                regionprops, prefix="object_", meta=self.global_metadata
            )

            # Get all the metadata
            json_meta = morphocut.Call(json.dumps, meta, sort_keys=True, default=str)

            # Publish the json containing all the metadata to via MQTT to Node-RED
            morphocut.Call(
                self.imaging_client.client.publish,
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
                self.imaging_client.client.publish,
                "status/segmentation/object_id",
                object_id,
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

    ################################################################################
    # While loop for capturing commands from Node-RED
    ################################################################################

    def run(self):
        """This is the function that needs to be started to create a thread

        This function runs for perpetuity. For now, it has no exit methods
        (hence no cleanup is performed on exit/kill). However, atexit can
        probably be used for this. See https://docs.python.org/3.8/library/atexit.html
        Eventually, the __del__ method could be used, if this module is
        made into a class.
        """
        while not stop_event.is_set():
            # TODO This should probably be a state machine, with the various transition between states made clear
            ############################################################################
            # Image Event
            ############################################################################
            if self.imaging_client.command == "image":

                # Publish the status "Start" to via MQTT to Node-RED
                self.imaging_client.client.publish(
                    "status/imager", "Will do my best dude"
                )

                # Get duration to wait before an image from the different received arguments
                sleep_before = int(args.split(" ")[0])

                # Get number of step in between two images from the different received arguments
                nb_step = int(args.split(" ")[1])

                # Get the number of frames to image from the different received arguments
                nb_frame = int(args.split(" ")[2])

                # Get the segmentation status (true/false) from the different received arguments
                segmentation = str(args.split(" ")[3])

                # Sleep a duration before to start acquisition
                time.sleep(sleep_before)

                # Publish the status "Start" to via MQTT to Node-RED
                self.imaging_client.client.publish("status/imager", "Start")

                # Set the LEDs as Blue
                planktoscope.light.setRGB(0, 0, 255)

                # TODO This logic here should be changed or at least evaluated to see if it still makes sense
                # Spoiler alert: it doesn't
                # We need a way to evaluate how long the pumping will take and go from there
                # Also, we need to get rid of the check on the last command received
                # Maybe a local variable to control the state machine would be more appropriate
                # Pump duing a given number of steps (in between each image)
                self.imaging_client.client.publish(
                    "actuator/pump", "FORWARD " + nb_step
                )
                for i in range(nb_step):

                    # If the command is still image - pump a defined nb of steps
                    if self.imaging_client.command == "image":
                        # The flowrate is fixed for now.
                        time.sleep(0.01)

                    # If the command isn't image anymore - break
                    else:
                        self.imaging_client.client.publish("actuator/pump", "stop")
                        break

                # Set the LEDs as Green
                planktoscope.light.setRGB(0, 255, 0)

                while True:

                    # Set the LEDs as Cyan
                    planktoscope.light.setRGB(0, 255, 255)

                    # Increment the counter
                    counter += 1

                    # Get datetime
                    datetime_tmp = datetime.now().strftime("%H_%M_%S_%f")

                    # Print datetime
                    logger.info(datetime_tmp)

                    # Define the filename of the image
                    filename = os.path.join(
                        "/home/pi/PlanktonScope/tmp", datetime_tmp + ".jpg"
                    )

                    # Capture an image with the proper filename
                    self.camera.capture(filename)

                    # Set the LEDs as Green
                    planktoscope.light.setRGB(0, 255, 0)

                    # Publish the name of the image to via MQTT to Node-RED

                    self.imaging_client.client.publish(
                        "status/imager", datetime_tmp + ".jpg has been imaged."
                    )

                    # Set the LEDs as Blue
                    planktoscope.light.setRGB(0, 0, 255)

                    # Pump during a given nb of steps
                    for i in range(nb_step):
                        # TODO This should call the stepper control thread instead of stepping by itself
                        # Actuate the pump for one step in the FORWARD direction
                        pump_stepper.onestep(
                            direction=stepper.FORWARD, style=stepper.DOUBLE
                        )

                        # The flowrate is fixed for now.
                        time.sleep(0.01)

                    # Wait a fixed delay which set the framerate as < than 2 imag/sec
                    time.sleep(0.5)

                    # Set the LEDs as Green
                    planktoscope.light.setRGB(0, 255, 0)

                    ####################################################################
                    # If counter reach the number of frame, break
                    if counter > nb_frame:

                        # Publish the status "Completed" to via MQTT to Node-RED
                        self.imaging_client.client.publish("status/imager", "Completed")

                        # Release the pump steppers to stop power draw
                        pump_stepper.release()

                        if segmentation == "True":

                            # Publish the status "Start" to via MQTT to Node-RED
                            self.imaging_client.client.publish(
                                "status/segmentation", "Start"
                            )

                            # Start the MorphoCut Pipeline
                            pipe.run()

                            # remove directory
                            # shutil.rmtree(import_path)

                            # Publish the status "Completed" to via MQTT to Node-RED
                            self.imaging_client.client.publish(
                                "status/segmentation", "Completed"
                            )

                            # Set the LEDs as White
                            planktoscope.light.setRGB(255, 255, 255)

                            # cmd = os.popen("rm -rf /home/pi/PlanktonScope/tmp/*.jpg")

                            # Let it happen
                            time.sleep(1)

                            # Set the LEDs as Green
                            planktoscope.light.setRGB(0, 255, 0)

                            # End if(segmentation == "True"):

                        # Change the command to not re-enter in this while loop
                        self.imaging_client.command = "wait"

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 255)

                        # Reset the counter to 0
                        counter = 0

                        break

                    ####################################################################
                    # If a new received command isn't "image", break this while loop
                    if self.imaging_client.command != "image":
                        # TODO This should be a call to the stepper thread.
                        # Release the pump steppers to stop power draw
                        pump_stepper.release()

                        # Print status
                        logger.info("The imaging has been interrupted.")

                        # Publish the status "Interrupted" to via MQTT to Node-RED
                        self.imaging_client.client.publish(
                            "status/imager", "Interrupted"
                        )

                        # Set the LEDs as Green
                        planktoscope.light.setRGB(0, 255, 0)

                        # Reset the counter to 0
                        counter = 0

                        break

            else:
                # Set the LEDs as Black
                planktoscope.light.setRGBOff()
                # Its just waiting to receive command from Node-RED
                time.sleep(1)
                # Set the LEDs as White
                planktoscope.light.setRGB(255, 255, 255)
                # Its just waiting to receive command from Node-RED
                time.sleep(1)

            
        logger.info("Shutting down the imager process")
