"""mqtt provides an MJPEG+MQTT API for camera interaction."""

import json
import os
import threading
import time
import typing

import loguru

from planktoscope import mqtt as messaging
from planktoscope.camera import hardware, mjpeg

loguru.logger.info("planktoscope.camera is loaded")


class Worker(threading.Thread):
    """Runs a camera with live MJPEG preview and an MQTT API for adjusting camera settings.

    Attribs:
        camera: the underlying camera exposed by this MQTT API. Don't access it until the
          camera_checked event has been set!
        camera_checked: when this event is set, either the camera is connected or has been
          determined to be missing.
    """

    def __init__(self, mjpeg_server_address: tuple[str, int] = ("", 8000)) -> None:
        """Initialize the backend.

        Args:
            mqtt_client: an MQTT client.
            exposure_time: the default value for initializing the camera's exposure time.

        Raises:
            ValueError: one or more values in the hardware config file are of the wrong type.
        """
        super().__init__(name="camera")

        settings = hardware.SettingsValues(
            auto_exposure=False,
            exposure_time=125,  # the default (minimum) exposure time in the PlanktoScope GUI
            image_gain=1.0,  # the default ISO of 100 in the PlanktoScope GUI
            brightness=0.0,  # the default "normal" brightness
            contrast=1.0,  # the default "normal" contrast
            auto_white_balance=False,  # the default setting in the PlanktoScope GUI
            white_balance_gains=hardware.WhiteBalanceGains(
                # the default gains from the default v2.5 hardware config
                red=2.4,
                blue=1.35,
            ),
            sharpness=0,  # disable the default "normal" sharpening level
            jpeg_quality=95,  # trade off between image file size and quality
        )
        # Settings
        if os.path.exists("/home/pi/PlanktoScope/hardware.json"):
            # load hardware.json
            with open("/home/pi/PlanktoScope/hardware.json", "r", encoding="utf-8") as config_file:
                hardware_config = json.load(config_file)
                loguru.logger.debug(
                    f"Loaded hardware configuration file: {hardware_config}",
                )
                settings = settings.overlay(hardware.config_to_settings_values(hardware_config))
        else:
            loguru.logger.info(
                "The hardware configuration file doesn't exist, using default settings: "
                + f"{settings}"
            )

        # I/O
        self._preview_stream: hardware.PreviewStream = hardware.PreviewStream()
        self._mjpeg_server_address = mjpeg_server_address
        self.camera: typing.Optional[hardware.PiCamera] = hardware.PiCamera(
            self._preview_stream, initial_settings=settings
        )
        self.camera_checked = threading.Event()
        self._stop_event_loop = threading.Event()

    @loguru.logger.catch
    def run(self) -> None:
        """Start the camera and run the main event loop."""
        assert self.camera is not None

        loguru.logger.info("Initializing the camera with default settings...")
        try:
            self.camera.open()
        except RuntimeError:
            loguru.logger.exception("Couldn't open the camera - maybe it's disconnected?")
            self.camera = None
            self.camera_checked.set()
            return
        self.camera_checked.set()

        loguru.logger.info("Starting the MJPEG streaming server...")
        streaming_server = mjpeg.StreamingServer(self._preview_stream, self._mjpeg_server_address)
        streaming_thread = threading.Thread(target=streaming_server.serve_forever)
        streaming_thread.start()

        loguru.logger.info("Starting the MQTT backend...")
        # TODO(ethanjli): expose the camera settings over "camera/settings" instead! This requires
        # removing the "settings" action from the "imager/image" route which is a breaking change
        # to the MQTT API, so we'll do this later.
        mqtt = messaging.MQTT_Client(topic="imager/image", name="imager_camera_client")
        # TODO(ethanjli): allow an MQTT client to trigger this broadcast with an MQTT command. This
        # requires modifying the MQTT API (by adding a new route), and we'll want to make the
        # Node-RED dashboard query that route at startup, so we'll do this later.
        mqtt.client.publish("status/imager", json.dumps({"camera_name": self.camera.camera_name}))

        try:
            while not self._stop_event_loop.is_set():
                if not mqtt.new_message_received():
                    time.sleep(0.1)
                    continue
                loguru.logger.debug(mqtt.msg)
                if (message := mqtt.msg) is None:
                    continue
                self._receive_message(message)
                if (status_update := mqtt.read_message()) is not None:
                    mqtt.client.publish("status/imager", status_update)
        finally:
            loguru.logger.info("Stopping the MQTT API...")
            mqtt.shutdown()

            loguru.logger.info("Stopping the MJPEG streaming server...")
            streaming_server.shutdown()
            streaming_server.server_close()
            streaming_thread.join()

            loguru.logger.info("Stopping the camera...")
            self.camera.close()
            self.camera = None

            loguru.logger.success("Done shutting down!")

    @loguru.logger.catch
    def _receive_message(self, message: dict[str, typing.Any]) -> typing.Optional[str]:
        """Handle a single MQTT message.

        Returns a status update to broadcast.
        """
        assert self.camera is not None

        if message["topic"] != "imager/image" or message["payload"].get("action", "") != "settings":
            return None
        if "settings" not in message["payload"]:
            loguru.logger.error(f"Received message is missing field 'settings': {message}")
            return '{"status":"Camera settings error"}'

        loguru.logger.info("Updating camera settings...")
        settings = message["payload"]["settings"]
        try:
            converted_settings = _convert_settings(
                settings, self.camera.settings.white_balance_gains
            )
            _validate_settings(converted_settings)
        except (TypeError, ValueError) as e:
            loguru.logger.exception(
                f"Couldn't convert MQTT command to hardware settings: {settings}",
            )
            return json.dumps({"status": f"Error: {str(e)}"})

        self.camera.settings = converted_settings
        loguru.logger.success("Updated camera settings!")
        return '{"status":"Camera settings updated"}'

    def shutdown(self):
        """Stop processing new MQTT messages and gracefully stop working."""
        self._stop_event_loop.set()


def _convert_settings(
    command_settings: dict[str, typing.Any],
    default_white_balance_gains: typing.Optional[hardware.WhiteBalanceGains],
) -> hardware.SettingsValues:
    """Convert MQTT command settings to camera hardware settings.

    Args:
        command_settings: the settings to convert.
        default_white_balance_gains: white-balance gains to substitute for missing values if exactly
          one gain is provided.

    Raises:
        ValueError: at least one of the MQTT command settings is invalid.
    """
    # TODO(ethanjli): separate out the status from the error message in the MQTT API, so
    # that we can just directly use the error messages from the
    # `hardware.SettingsValues.validate()` method. That would be simpler; for now we're
    # trying to keep the MQTT API unchanged, so we return different ValueErrors.
    converted = hardware.SettingsValues()
    if "shutter_speed" in command_settings:
        try:
            exposure_time = int(command_settings["shutter_speed"])
        except (TypeError, ValueError) as e:
            raise ValueError("Shutter speed not valid") from e
        converted = converted._replace(exposure_time=exposure_time)
    converted = converted.overlay(_convert_image_gain_settings(command_settings))
    if "white_balance" in command_settings:
        if (awb := command_settings["white_balance"]) not in {"auto", "off"}:
            raise ValueError("White balance mode {awb} not valid")
        converted = converted._replace(auto_white_balance=awb != "off")
    converted = converted.overlay(
        _convert_white_balance_gain_settings(command_settings, default_white_balance_gains)
    )

    return converted


def _convert_image_gain_settings(
    command_settings: dict[str, typing.Any],
) -> hardware.SettingsValues:
    """Convert image gains in MQTT command settings to camera hardware settings.

    Args:
        command_settings: the settings to convert.

    Raises:
        ValueError: at least one of the MQTT command settings is invalid.
    """
    converted = hardware.SettingsValues()
    # TODO(ethanjli): now that we're using image_gain as the ISO, we should remove one of them
    # from the MQTT API (it could be better to keep ISO since it's tied to metadata, or it could
    # be better to remove ISO since ISO is a fictitious parameter (since the hardware doesn't
    # actually have ISO) and needs a conversion to the real image_gain parameter for the hardware).
    # Then we could delete this function. For now, we'll just redirect both to image_gain, with ISO
    # taking precedence when both are provided in the same command:
    if "image_gain" in command_settings:
        try:
            image_gain = float(command_settings["image_gain"]["analog"])
        except (ValueError, KeyError) as e:
            raise ValueError("Image gain not valid") from e
        converted = converted._replace(image_gain=image_gain)
    if "iso" in command_settings:
        try:
            iso = float(command_settings["iso"])
        except (TypeError, ValueError) as e:
            raise ValueError("Iso number not valid") from e
        converted = converted._replace(image_gain=iso / 100)

    return converted


def _convert_white_balance_gain_settings(
    command_settings: dict[str, typing.Any],
    # TODO(ethanjli): modify the PlanktoScope GUI to send both red and blue white balance values
    # together each time either is updated, and modify the MQTT API to require both values to be
    # always provided together. That would simplify the code here and remove the need to keep track
    # of previous white balance gains (which could be prone to getting into an inconsistent state
    # compared to the values shown in the GUI); we could maybe even delete this function afterwards.
    default_white_balance_gains: typing.Optional[hardware.WhiteBalanceGains],
) -> hardware.SettingsValues:
    """Convert white-balance gains in MQTT command settings to camera hardware settings.

    Args:
        command_settings: the settings to convert.
        default_white_balance_gains: white-balance gains to substitute for missing values if exactly
          one gain is provided.

    Raises:
        ValueError: at least one of the MQTT command settings is invalid.
    """
    converted = hardware.SettingsValues()
    if "white_balance_gain" not in command_settings:
        return converted

    # TODO(ethanjli): change the MQTT API use normal white-balance gains instead of the gains which
    # are multiplied by 100, since the PlanktoScope GUI shows them without the multiplication by 100
    # anyways. That will make the flow of values simpler and easier to follow, since we won't need
    # to transform them on both sides of the API.
    try:
        red_gain = float(command_settings["white_balance_gain"]["red"]) / 100
    except (TypeError, ValueError) as e:
        raise ValueError("White balance gain not valid") from e
    except KeyError as e:
        if default_white_balance_gains is None:
            raise ValueError("White balance gain not valid") from e
        red_gain = default_white_balance_gains.red
    try:
        blue_gain = float(command_settings["white_balance_gain"]["blue"]) / 100
    except (TypeError, ValueError) as e:
        raise ValueError("White balance gain not valid") from e
    except KeyError as e:
        if default_white_balance_gains is None:
            raise ValueError("White balance gain not valid") from e
        blue_gain = default_white_balance_gains.blue
    return converted._replace(
        white_balance_gains=hardware.WhiteBalanceGains(red=red_gain, blue=blue_gain)
    )


# TODO(ethanjli): separate out the status from the error message in the MQTT API, so
# that we can just directly use the error messages from the `hardware.SettingsValues.validate()`
# method, and then we can delete this function. That would be simpler; for now we're trying to keep
# the MQTT API unchanged, so we have this wrapper to return different ValueErrors.
def _validate_settings(settings: hardware.SettingsValues) -> None:
    """Check validity of camera hardware settings.

    Raises:
        ValueError: at least one of the MQTT command settings is invalid.
    """
    if validation_errors := settings.validate():
        loguru.logger.error(
            f"Invalid camera settings requested: {'; '.join(validation_errors)}",
        )
        erroneous_field, _ = validation_errors[0].split(" out of range", 1)
        error_message_mappings = {
            "Exposure time": "Shutter speed",
            "Image gain": "Iso number",
            "Red white-balance gain": "White balance gain",
            "Blue white-balance gain": "White balance gain",
        }
        raise ValueError(
            f"{error_message_mappings.get(erroneous_field, erroneous_field)} not valid",
        )
