################################################################################
# Practical Libraries
################################################################################

# Logger library compatible with multiprocessing
from loguru import logger

# Library for path and filesystem manipulations
import os

# Library to get date and time for folder name and filename
import datetime
import time

# Library to control the RaspiMJPEG process
import subprocess  # nosec


################################################################################
# Class for the communication with RaspiMJPEG
################################################################################
class raspimjpeg(object):
    def __init__(self, *args, **kwargs):
        self.__configfile = "/home/pi/PlanktonScope/scripts/raspimjpeg/raspimjpeg.conf"
        self.__binary = "/home/pi/PlanktonScope/scripts/raspimjpeg/bin/raspimjpeg"
        self.__statusfile = "/dev/shm/mjpeg/status_mjpeg.txt"  # nosec
        self.__pipe = "/dev/shm/mjpeg/FIFO"  # nosec
        self.__sensor_name = ""

        # make sure the status file exists and is empty
        if not os.path.exists(self.__statusfile):
            logger.debug("The status file does not exists, creating now")
            # create the path!
            os.makedirs(os.path.dirname(self.__statusfile), exist_ok=True)

        # If the file does not exists, creates it
        # otherwise make sure it's empty
        with open(self.__statusfile, "w") as file:
            file.write("")

        # make sure the pipe exists
        if not os.path.exists(self.__pipe):
            logger.debug("The pipe does not exists, creating now")
            os.makedirs(os.path.dirname(self.__pipe), exist_ok=True)
            os.mkfifo(self.__pipe)

        # make sure the config file exists
        if not os.path.exists(self.__configfile):
            logger.error("The config file does not exists!")

    def start(self, force=False):
        logger.debug("Starting up raspimjpeg")
        if force:
            # let's kill all rogue Raspimjpeg first
            try:
                subprocess.run(  # nosec
                    "sudo killall -9 raspimjpeg".split(),
                    shell=True,
                    timeout=1,
                    check=True,
                )
            except Exception as e:
                logger.exception(f"Killing Raspimjpeg failed because of {e}")
        # The input to this call are perfectly controlled
        # hence the nosec comment to deactivate bandit error
        self.__process = subprocess.Popen(  # nosec
            [self.__binary, "-c", self.__configfile],
            stdout=subprocess.PIPE,
            bufsize=1,  # means line buffered
            text=True,
        )
        # self.__process.stdout can be read as a file

        # This will set the reads on stdout to be non-blocking
        os.set_blocking(self.__process.stdout.fileno(), False)

        try:
            name_string = self.__parse_output_for("Camera Name")
            self.__sensor_name = name_string.rsplit(" ", 1)[1].upper().rstrip()
        except TimeoutError as e:
            logger.exception(
                f"A timeout happened while waiting for RaspiMJPEG to start: {e}"
            )
            raise e

        try:
            width_string = self.__parse_output_for("Camera Max Width:")
            self.__width = width_string.rsplit(" ", 1)[1]
        except TimeoutError as e:
            logger.exception(
                f"A timeout happened while waiting for RaspiMJPEG to start: {e}"
            )
            raise e

        try:
            height_string = self.__parse_output_for("Camera Max Height")
            self.__height = height_string.rsplit(" ", 1)[1]
        except TimeoutError as e:
            logger.exception(
                f"A timeout happened while waiting for RaspiMJPEG to start: {e}"
            )
            raise e

        try:
            self.__wait_for_output("Starting command loop")
        except TimeoutError as e:
            logger.exception(
                f"A timeout happened while waiting for RaspiMJPEG to start: {e}"
            )
            raise e

    def status(self):
        return self.__get_status()

    def __parse_output_for(self, text, timeout=5):
        """Blocking, waiting for specific output from process

        Continously poll the process stdout file object.

        Args:
            text (string): String to wait for
            timeout (int, optional): Timeout duration in seconds. Defaults to 5.

        Raises:
            TimeoutError: A timeout happened before the required output showed up
        """
        logger.debug(f"Parsing the output for {text} for {timeout}s")
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

        break_loop = False
        while True:
            for nextline in self.__process.stdout:
                logger.trace(f"last read line is {nextline}")
                if nextline.startswith(text):
                    return nextline

            if wait_until < datetime.datetime.now():
                # The timeout has been reached!
                logger.error("A timeout has occured waiting for a RaspiMJPEG answer")
                raise TimeoutError

            time.sleep(0.1)

    def __wait_for_output(self, output, timeout=5):
        """Blocking, waiting for specific output from process

        Continously poll the process stdout file object.

        Args:
            output (string): String to wait for
            timeout (int, optional): Timeout duration in seconds. Defaults to 5.

        Raises:
            TimeoutError: A timeout happened before the required output showed up
        """
        logger.debug(f"Waiting for {output} for {timeout}s")
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

        break_loop = False
        while True:
            for nextline in self.__process.stdout:
                logger.trace(f"last read line is {nextline}")
                if nextline.startswith("Error:"):
                    logger.error(f"RaspiMJPEG error: {nextline}")
                elif nextline.startswith(output):
                    return

            if wait_until < datetime.datetime.now():
                # The timeout has been reached!
                logger.error("A timeout has occured waiting for a RaspiMJPEG answer")
                raise TimeoutError

            time.sleep(0.1)

    def __get_status(self):
        """Open and return the status file content

        Returns:
            string: status of the process
        """
        logger.trace("Getting the status file")
        try:
            with open(self.__statusfile, "r") as status:
                status = status.read()
            logger.trace(f"Read {status} from {self.__statusfile}")
            return status
        except FileNotFoundError as e:
            logger.error(
                f"The status file was not found, make sure the filesystem has not been corrupted"
            )
            return ""

    def __wait_for_status(self, status, timeout=5):
        """Wait for a specific status. Blocking, obviously.

        Args:
            status (string): The status to wait for
        """
        logger.debug(f"Waiting for {status} for {timeout}s")
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

        message = self.__get_status()

        while True:
            if message.startswith(status):
                return

            if wait_until < datetime.datetime.now():
                # The timeout has been reached!
                logger.error("A timeout has occured waiting for a RaspiMJPEG answer")
                raise TimeoutError

            time.sleep(0.1)
            logger.debug(f"not {status} yet")
            message = self.__get_status()

    def __send_command(self, command):
        """Sends a command to the RaspiMJPEG process

        Args:
            command (string): the command string to send
        """
        # TODO add check to make sure the pipe is open on the other side, otherwise this is blocking.
        # Maybe just check that self.__process is still alive? :-)
        logger.debug(f"Sending the command [{command}] to raspimjpeg")
        with open(self.__pipe, "w") as pipe:
            pipe.write(f"{command}\n")

    @property
    def sensor_name(self):
        """Sensor name of the connected camera

        Returns:
            string: Sensor name. One of OV5647 (cam v1), IMX219 (cam v2.1), IMX477(ca HQ)
        """
        return self.__sensor_name

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def resolution(self):
        return self.__resolution

    @resolution.setter
    def resolution(self, resolution):
        """Change the camera image resolution

        For a full FOV, allowable resolutions are:
        - (3280,2464), (1640,1232), (1640,922) for Camera V2.1
        - (2028,1520), (4056,3040) for HQ Camera


        Args:
            resolution (tuple of int): resolution to set the camera to
        """
        logger.debug(f"Setting the resolution to {resolution}")
        if resolution in [
            (3280, 2464),
            (1640, 1232),
            (1640, 922),
            (2028, 1520),
            (4056, 3040),
        ]:
            self.__resolution = resolution
            self.__send_command(
                f"px 1640 1232 15 15 {self.__resolution[0]} {self.__resolution[1]} 01"
            )
        else:
            logger.error(f"The resolution specified ({resolution}) is not valid")
            raise ValueError

    @property
    def iso(self):
        return self.__iso

    @iso.setter
    def iso(self, iso):
        """Change the camera iso number

        Iso number will be rounded to the closest one of
        0, 100, 200, 320, 400, 500, 640, 800.
        If 0, Iso number will be chosen automatically by the camera

        Args:
            iso (int): Iso number
        """
        logger.debug(f"Setting the iso number to {iso}")

        if 0 <= iso <= 800:
            self.__iso = iso
            self.__send_command(f"is {self.__iso}")
            self.__wait_for_output("Change: iso")
        else:
            logger.error(f"The ISO number specified ({iso}) is not valid")
            raise ValueError

    @property
    def shutter_speed(self):
        return self.__shutter_speed

    @shutter_speed.setter
    def shutter_speed(self, shutter_speed):
        """Change the camera shutter speed

        Args:
            shutter_speed (int): shutter speed in µs
        """
        logger.debug(f"Setting the shutter speed to {shutter_speed}")
        if 0 < shutter_speed < 5000:
            self.__shutter_speed = shutter_speed
            self.__send_command(f"ss {self.__shutter_speed}")
            self.__wait_for_output("Change: shutter_speed")
        else:
            logger.error(f"The shutter speed specified ({shutter_speed}) is not valid")
            raise ValueError

    @property
    def exposure_mode(self):
        return self.__exposure_mode

    @exposure_mode.setter
    def exposure_mode(self, mode):
        """Change the camera exposure mode

        Is one of off, auto, night, nightpreview, backlight, spotlight,
        sports, snow, beach, verylong, fixedfps, antishake, fireworks

        Args:
            mode (string): exposure mode to use
        """
        logger.debug(f"Setting the exposure mode to {mode}")
        if mode in [
            "off",
            "auto",
            "night",
            "nightpreview",
            "backlight",
            "spotlight",
            "sports",
            "snow",
            "beach",
            "verylong",
            "fixedfps",
            "antishake",
            "fireworks",
        ]:
            self.__exposure_mode = mode
            self.__send_command(f"em {self.__exposure_mode}")
        else:
            logger.error(f"The exposure mode specified ({mode}) is not valid")
            raise ValueError

    @property
    def white_balance(self):
        return self.__white_balance

    @white_balance.setter
    def white_balance(self, mode):
        """Change the camera white balance mode

        Is one of off, auto, sun, cloudy, shade, tungsten,
        fluorescent, incandescent, flash, horizon

        Args:
            mode (string): white balance mode to use
        """
        logger.debug(f"Setting the white balance mode to {mode}")
        if mode in [
            "off",
            "auto",
            "sun",
            "cloudy",
            "shade",
            "tungsten",
            "fluorescent",
            "incandescent",
            "flash",
            "horizon",
        ]:
            self.__white_balance = mode
            self.__send_command(f"wb {self.__white_balance}")
        else:
            logger.error(
                f"The camera white balance mode specified ({mode}) is not valid"
            )
            raise ValueError

    @property
    def white_balance_gain(self):
        return self.__white_balance_gain

    @white_balance_gain.setter
    def white_balance_gain(self, gain):
        """Change the camera white balance gain

            The gain value should be a int between 0 and 300. By default the camera
            is set to use 150 both for the red and the blue gain.

        Args:
            gain (tuple of int): Red gain and blue gain to use
        """
        logger.debug(f"Setting the white balance mode to {gain}")
        if (0 < gain[0] < 800) and (0 < gain[1] < 800):
            self.__white_balance_gain = gain
            self.__send_command(
                f"ag {self.__white_balance_gain[0]} {self.__white_balance_gain[1]}"
            )
        else:
            logger.error(
                f"The camera white balance gain specified ({gain}) is not valid"
            )
            raise ValueError

    @property
    def image_quality(self):
        return self.__image_quality

    @image_quality.setter
    def image_quality(self, image_quality):
        """Change the output image quality

        Args:
            image_quality (int): image quality [0,100]
        """
        logger.debug(f"Setting image quality to {image_quality}")
        if 0 <= image_quality <= 100:
            self.__image_quality = image_quality
            self.__send_command(f"ss {self.__image_quality}")
        else:
            logger.error(
                f"The output image quality specified ({image_quality}) is not valid"
            )
            raise ValueError

    @property
    def preview_quality(self):
        return self.__preview_quality

    @preview_quality.setter
    def preview_quality(self, preview_quality):
        """Change the preview image quality

        Args:
            preview_quality (int): image quality [0,100]
        """
        logger.debug(f"Setting preview quality to {preview_quality}")
        if 0 <= preview_quality <= 100:
            self.__preview_quality = preview_quality
            self.__send_command(f"pv {self.__preview_quality} 512 01")
        else:
            logger.error(
                f"The preview image quality specified ({preview_quality}) is not valid"
            )
            raise ValueError

    def capture(self, path="", timeout=5):
        """Capture an image. Blocks for timeout seconds(5 by default) until the image is captured.

        Args:
            path (str, optional): Path to image file. Defaults to "".
            timeout (int, optional): Timeout duration in seconds. Defaults to 5.

        Raises:
            TimeoutError: A timeout happened before the required output showed up
        """
        logger.debug(f"Capturing an image to {path}")
        if path == "":
            self.__send_command(f"im")
        else:
            self.__send_command(f"im {path}")
        time.sleep(0.1)

        self.__wait_for_output("Capturing image", timeout / 2)
        self.__wait_for_output("Ready", timeout / 2)

    def stop(self):
        """Halt and release the camera."""
        logger.debug("Releasing the camera now")
        self.__send_command(f"ru 0")

    def close(self):
        """Kill the process."""
        logger.debug("Killing raspimjpeg in a nice way")
        self.__process.terminate()
        self.__process.wait()

    def kill(self):
        """Kill the process."""
        logger.debug("Killing raspimjpeg in a very dirty way")
        self.__process.terminate()
