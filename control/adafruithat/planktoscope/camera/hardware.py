"""hardware provides basic I/O abstractions for camera hardware."""

import io
import threading
import typing

import loguru
import picamera2  # type: ignore
import typing_extensions
from picamera2 import encoders, outputs
from readerwriterlock import rwlock


class StreamConfig(typing.NamedTuple):
    """Values for stream configuration performed exactly once, before the camera starts.

    Fields with `None` values should be ignored as if they were not set.
    """

    # The width & height (in pixels) of captured (non-preview) images; defaults to the max allowed
    # size for the camera sensor:
    capture_size: typing.Optional[tuple[int, int]] = None
    # The width & height (in pixels) of camera preview; defaults to the max allowed size for the
    # camera sensor:
    preview_size: typing.Optional[tuple[int, int]] = None
    # The bitrate (in bits/sec) of the preview stream; defaults to a bitrate automatically
    # calculated for a high-quality stream:
    preview_bitrate: typing.Optional[int] = None
    # The number of frame buffers to allocate in memory:
    # Note(ethanjli): from testing, it seems that we need at least three buffers to allow the
    # preview to continue receiving frames smoothly from the "lores" stream while a buffer is
    # reserved for saving an image from the "main" stream.
    buffer_count: int = 3
    # Whether to allow the last queued frame to be returned for a capture, even if that frame was
    # saved before the capture request:
    queue: bool = False

    def overlay(self, updates: "StreamConfig") -> "StreamConfig":
        """Create a new instance where provided non-`None` values overwrite existing values."""
        # pylint complains that this namedtuple has no `_asdict()` method even though mypy is fine;
        # this is a false positive:
        # pylint: disable-next=no-member
        return self._replace(
            **{key: value for key, value in updates._asdict().items() if value is not None}
        )


def _picamera2_to_stream_config(config: dict[str, typing.Any]) -> StreamConfig:
    """Create a StreamConfig from a picamera2 pre-start configuration.

    Raises:
        KeyError: the configuration does not contain the required fields.
        ValueError: the configuration does not contain the required fields or values.
    """
    return StreamConfig(
        capture_size=config["main"]["size"],
        preview_size=config["lores"]["size"],
        buffer_count=config["buffer_count"],
        queue=config["queue"],
    )


class WhiteBalanceGains(typing.NamedTuple):
    """Manual white balance gains."""

    red: float
    blue: float


class SettingsValues(typing.NamedTuple):
    """Values for camera settings adjustable anytime after the camera is configured.

    Fields with `None` values should be ignored as if they were not set.
    """

    # picamera2 controls
    auto_exposure: typing.Optional[bool] = None
    exposure_time: typing.Optional[int] = None  # μs; must be within frame_duration_limits
    frame_duration_limits: typing.Optional[tuple[int, int]] = None  # μs
    image_gain: typing.Optional[float] = None  # must be within [0.0, 16.0]
    brightness: typing.Optional[float] = None  # must be within [-1.0, 1.0]
    contrast: typing.Optional[float] = None  # must be within [0.0, 32.0]
    auto_white_balance: typing.Optional[bool] = None
    white_balance_gains: typing.Optional[WhiteBalanceGains] = None  # must be within [0.0, 32.0]
    sharpness: typing.Optional[float] = None  # must be within [0.0, 16.0]

    # picamera2 options
    jpeg_quality: typing.Optional[int] = None  # must be within [0, 95]

    # Note(ethanjli): we can also expose other settings/properties in a similar way, but we don't
    # need them yet and we're trying to minimize the amount of code we have to maintain, so for now
    # I haven't implemented them.

    def validate(self) -> list[str]:
        """Look for values which are invalid because they're out-of-range.

        Returns:
            A list of strings, each representing a validation error.
        """
        value: typing.Any = None
        errors = self._validate_exposure_time()
        if (value := self.image_gain) is not None and not 0.0 <= value <= 16.0:
            errors.append(f"Image gain out of range [0.0, 16.0]: {value}")
        if (value := self.brightness) is not None and not -1.0 <= value <= 1.0:
            errors.append(f"Brightness out of range [-1.0, 1.0]: {value}")
        if (value := self.contrast) is not None and not 0.0 <= value <= 32.0:
            errors.append(f"Contrast out of range [0.0, 32.0]: {value}")
        if (value := self.white_balance_gains) is not None and not 0.0 <= value.red <= 32.0:
            errors.append(f"Red white-balance gain out of range [0.0, 32.0]: {value.red}")
        if (value := self.white_balance_gains) is not None and not 0.0 <= value.blue <= 32.0:
            errors.append(f"Blue white-balance gain out of range [0.0, 32.0]: {value.blue}")
        if (value := self.sharpness) is not None and not 0.0 <= value <= 16.0:
            errors.append(f"Sharpness out of range [0.0, 16.0]: {value}")
        if (value := self.jpeg_quality) is not None and not 0 <= value <= 95:
            errors.append(f"JPEG quality out of range [0, 95]: {value}")

        return errors

    def _validate_exposure_time(self) -> list[str]:
        """Check whether exposure_time is consistent with frame_duration_limits."""
        if (value := self.exposure_time) is None:
            return []

        if (limits := self.frame_duration_limits) is None:
            if value < 0:
                return [f"Exposure time out of range [0, +Inf]: {value}"]
            return []

        # This is a pylint false-positive, since mypy knows `limits` is an unpackable tuple:
        min_limit, max_limit = limits  # pylint: disable=unpacking-non-sequence
        if not min_limit <= value <= max_limit:
            return [f"Exposure time out of range [{min_limit}, {max_limit}]: {value}"]

        return []

    def has_values(self) -> bool:
        """Check whether any values are non-`None`."""
        # pylint complains that this namedtuple has no `_asdict()` method even though mypy is fine;
        # this is a false positive:
        # pylint: disable-next=no-member
        return any(value is not None for value in self._asdict().values())

    def overlay(self, updates: "SettingsValues") -> "SettingsValues":
        """Create a new instance where provided non-`None` values overwrite existing values.

        This is intended to make it easy to combine existing settings with new settings.
        """
        # pylint complains that this namedtuple has no `_asdict()` method even though mypy is fine;
        # this is a false positive:
        # pylint: disable-next=no-member
        return self._replace(
            **{key: value for key, value in updates._asdict().items() if value is not None}
        )

    def as_picamera2_controls(self) -> dict[str, typing.Any]:
        """Create an equivalent dict of values for picamera2's camera controls."""
        result = {
            "AeEnable": self.auto_exposure,
            "ExposureTime": self.exposure_time,
            "AnalogueGain": self.image_gain,
            "Brightness": self.brightness,
            "Contrast": self.contrast,
            "AwbEnable": self.auto_white_balance,
            "ColourGains": self.white_balance_gains,
            "Sharpness": self.sharpness,
        }
        return {key: value for key, value in result.items() if value is not None}

    def as_picamera2_options(self) -> dict[str, typing.Any]:
        """Create an equivalent dict of values suitable for picamera2's camera options."""
        result = {"quality": self.jpeg_quality}
        return {key: value for key, value in result.items() if value is not None}


def _picamera2_to_settings_values(config: dict[str, typing.Any]) -> SettingsValues:
    """Create a SettingsValues from a picamera2 pre-start configuration.

    Raises:
        KeyError: the configuration does not contain the required fields or values.
    """
    frame_duration_limits = config["controls"]["FrameDurationLimits"]
    return SettingsValues(frame_duration_limits=frame_duration_limits)


def config_to_settings_values(config: dict[str, typing.Any]) -> SettingsValues:
    """Create a SettingsValues from a hardware.json configuration."""
    result = SettingsValues()
    # TODO(ethanjli): add exposure time (previously called "shutter speed") and image gain
    # (previously called "iso" but with a different scaling factor) and auto_white_balance to the
    # hardware.json config. Maybe also add jpeg_quality? For details, refer to
    # https://github.com/PlanktoScope/PlanktoScope/issues/290
    if "red_gain" in config or "blue_gain" in config:
        try:
            red_gain = float(config["red_gain"])
            blue_gain = float(config["blue_gain"])
        except KeyError:
            loguru.logger.warning(
                "One of the white balance gains is unspecified! Both gains will be ignored.",
            )
            return result
        except (TypeError, ValueError):
            loguru.logger.warning(
                "White balance gains have incorrect type! Both gains will be ignored.",
            )
            return result
        result = result.overlay(
            SettingsValues(white_balance_gains=WhiteBalanceGains(red=red_gain, blue=blue_gain))
        )
    return result


class PiCamera:
    """A thread-safe and type-safe wrapper around a picamera2-based camera.

    The camera has two streams: a capture stream (for manually triggering image capture) and a
    preview stream (which is continuously updated in the background).
    """

    def __init__(
        self,
        preview_output: io.BufferedIOBase,
        stream_config: StreamConfig = StreamConfig(
            preview_size=(960, 720),
            # We'll never reach 80 Mbps of bandwidth usage because the RPi's network links don't
            # have enough bandwidth; instead, we'll have higher-quality frames at lower framerates:
            preview_bitrate=80 * 1000000,
            buffer_count=3,
        ),
        initial_settings: SettingsValues = SettingsValues(),
    ) -> None:
        """Set up state needed to initialize the camera, but don't actually start the camera yet.

        Args:
            preview_output: an image stream which this `PiCamera` instance will write camera preview
              images to once the camera is started.
            stream_config: configuration of camera output streams.
            initial_settings: any camera settings to initialize the camera with.
        """
        # Settings & configuration
        self._settings_lock = rwlock.RWLockWrite()
        self._stream_config = stream_config
        self._cached_settings = initial_settings

        # I/O:
        self._preview_output = preview_output
        self._camera: typing.Optional[picamera2.Picamera2] = None

    def open(self) -> None:
        """Start the camera in the background, including output to the preview stream.

        Blocks until the camera has started.
        """
        loguru.logger.debug("Initializing the camera...")
        try:
            self._camera = picamera2.Picamera2()
        except RuntimeError as e:
            self._camera = None
            raise RuntimeError("Could not initialize the camera!") from e

        loguru.logger.debug("Configuring the camera...")
        main_config: dict[str, typing.Any] = {}
        if (main_size := self._stream_config.capture_size) is not None:
            main_config["size"] = main_size
        lores_config: dict[str, typing.Any] = {}
        if (lores_size := self._stream_config.preview_size) is not None:
            lores_config["size"] = lores_size
        # Note(ethanjli): we use the `create_still_configuration` to get the best defaults for still
        # images from the "main" stream:
        config = self._camera.create_still_configuration(
            main_config,
            lores_config,
            buffer_count=self._stream_config.buffer_count,
            queue=self._stream_config.queue,
        )
        loguru.logger.debug(f"Camera configuration: {config}")
        self._camera.configure(config)
        with self._settings_lock.gen_wlock():
            self._stream_config = self._stream_config.overlay(_picamera2_to_stream_config(config))
            loguru.logger.debug(f"Final stream configuration: {self._stream_config}")

        initial_settings = self._cached_settings.overlay(_picamera2_to_settings_values(config))
        loguru.logger.debug("Initializing camera settings...")
        self.settings = initial_settings

        loguru.logger.debug("Starting the camera...")
        self._camera.start_recording(
            # Note(ethanjli): for compatibility with the RPi 4 (which must use YUV420 for "lores"
            # stream output), we cannot use `JpegEncoder` (which only accepts RGB, not YUV); for
            # details, refer to Table 1 on page 59 of the picamera2 manual. So we must use
            # `MJPEGEncoder` instead:
            encoders.MJPEGEncoder(bitrate=self._stream_config.preview_bitrate),
            outputs.FileOutput(self._preview_output),
            # If we specify quality, it overrides the bitrate, contrary to what the picamera2 docs
            # say (refer to
            # github.com/raspberrypi/picamera2/blob/main/picamera2/encoders/mjpeg_encoder.py#L23):
            # quality=encoders.Quality.VERY_HIGH,
            name="lores",
        )

    @property
    def stream_config(self) -> StreamConfig:
        """An immutable copy of the camera streams configuration."""
        with self._settings_lock.gen_rlock():
            return self._stream_config

    @property
    def settings(self) -> SettingsValues:
        """Adjustable camera settings values."""
        with self._settings_lock.gen_rlock():
            return self._cached_settings

    @settings.setter
    def settings(self, updates: SettingsValues) -> None:
        """Update adjustable camera settings from all provided non-`None` values.

        Fields provided with `None` values are ignored. If any of the provided non-`None` values is
        invalid (e.g. out-of-range), none of the settings will be changed.

        Raises:
            RuntimeError: the method was called before the camera was started, or after it was
              closed.
            ValueError: some of the provided values are out of the allowed ranges.
        """
        if not updates.has_values():
            return
        if self._camera is None:
            raise RuntimeError("The camera has not been started yet!")

        loguru.logger.debug(f"Applying camera settings updates: {updates}")
        with self._settings_lock.gen_wlock():
            new_values = self._cached_settings.overlay(updates)
            loguru.logger.debug(f"New camera settings will be: {new_values}")
            if errors := new_values.validate():
                raise ValueError(f"Invalid settings: {'; '.join(errors)}")
            loguru.logger.debug(f"Setting picamera2 controls: {new_values.as_picamera2_controls()}")
            self._camera.set_controls(new_values.as_picamera2_controls())
            for key, value in updates.as_picamera2_options().items():
                self._camera.options[key] = value
            self._cached_settings = new_values

    @property
    def sensor_name(self) -> str:
        """Name of the camera sensor.

        Returns:
            Usually one of: `IMX219` (RPi Camera Module 2, used in PlanktoScope hardware v2.1)
            or `IMX477` (RPi High Quality Camera, used in PlanktoScope hardware v2.3+).

        Raises:
            RuntimeError: the method was called before the camera was started, or after it was
              closed.
        """
        if self._camera is None:
            raise RuntimeError("The camera has not been started yet!")

        model = self._camera.camera_properties["Model"]
        assert isinstance(model, str)
        return model.upper()

    @property
    def camera_name(self) -> str:
        """Name of the camera model.

        Returns:
            "Camera v2.1" for an IMX219 sensor, "HQ Camera" for an IMX477 sensor, or
            "Not recognized" otherwise.

        Raises:
            RuntimeError: the method was called before the camera was started, or after it was
              closed.
        """
        if self._camera is None:
            raise RuntimeError("The camera has not been started yet!")

        camera_names = {
            "IMX219": "Camera v2.1",
            # Note(ethanjli): Currently the PlanktoScope GUI requires this to be "HQ Camera" rather
            # than "Camera HQ".
            "IMX477": "HQ Camera",
        }
        return camera_names.get(self.sensor_name, "Not recognized")

    def capture_file(self, path: str) -> None:
        """Capture an image from the main stream (in full resolution) and save it as a file.

        Blocks until the image is fully saved.

        Args:
            path: The file path where the image should be saved.

        Raises:
            RuntimeError: the method was called before the camera was started, or after it was
              closed.
        """
        if self._camera is None:
            raise RuntimeError("The camera has not been started yet!")

        loguru.logger.debug(f"Capturing and saving image to {path}...")
        request = self._camera.capture_request()
        # The following lines are false-positives in pylint because they're dynamically-generated
        # members:
        request.save("main", path)  # pylint: disable=no-member
        loguru.logger.debug(
            f"Image metadata: {request.get_metadata()}"  # pylint: disable=no-member
        )
        request.release()  # pylint: disable=no-member

    def close(self) -> None:
        """Stop and close the camera.

        No more frames will be written to the preview output stream.

        The camera can be restarted after being closed by calling the `start()` method again.
        """
        if self._camera is None:
            return

        loguru.logger.debug("Stopping the camera...")
        # Note(ethanjli): when picamera2 itself crashes while recording in the background, calling
        # `stop_recording()` causes a deadlock! I don't know how to work around that deadlock; this
        # might be an upstream bug which we could fix by upgrading to RPi OS 12, or maybe we need to
        # file an issue with upstream (i.e. in the picamera2 GitHub repo...for now, we'll just try
        # to avoid causing crashes in picamera2 and worry about this problem another day 🤡
        self._camera.stop_recording()

        loguru.logger.debug("Closing the camera...")
        self._camera.close()
        self._camera = None
        self._cached_settings = SettingsValues()


class PreviewStream(io.BufferedIOBase):
    """A thread-safe stream of discrete byte buffers for use in live previews.

    This stream is designed to support at-most-once delivery, so no guarantees are made about
    delivery of every buffer to the consumers: a consumer will skip buffers when it's too busy
    overloaded/blocked. This is a design feature to prevent backpressure on certain consumers
    (e.g. from downstream clients sending the buffer across a network, when the buffer is a large
    image) from degrading stream quality for everyone.

    Note that no thread synchronization is managed for any buffer; consumers must avoid modifying
    the buffer once they have access to it.

    This stream can be used by anything which requires a [io.BufferedIOBase], assuming it never
    splits any buffer across multiple calls of the `write()` method.
    """

    def __init__(self) -> None:
        """Initialize the stream."""
        self._latest_buffer: typing.Optional[bytes] = None
        # Mutex to prevent data races between readers and writers:
        self._latest_buffer_lock = rwlock.RWLockWrite()
        # Condition variable to allow listeners to wait for a new buffer:
        self._available = threading.Condition()

    def write(self, buffer: typing_extensions.Buffer) -> int:
        """Write the byte buffer as the latest buffer in the stream.

        If readers are accessing the buffer when this method is called, then it may block for a
        while, in order to wait for those readers to finish.

        Returns:
            The length of the byte buffer written.
        """
        b = bytes(buffer)
        with self._latest_buffer_lock.gen_wlock():
            self._latest_buffer = b
        with self._available:
            self._available.notify_all()
        return len(b)

    def wait_next(self) -> None:
        """Wait until the next buffer is available.

        When called, this method blocks until it is awakened by a `update()` call in another
        thread. Once awakened, it returns.
        """
        with self._available:
            self._available.wait()

    def get(self) -> typing.Optional[bytes]:
        """Return the latest buffer in the stream."""
        with self._latest_buffer_lock.gen_rlock():
            return self._latest_buffer
