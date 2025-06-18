"""test_streamer is a test script to bring up an isolated camera preview stream on port 8000."""

import argparse
import threading
import time

import loguru
import picamera2  # type: ignore
from picamera2 import encoders, outputs

from . import hardware, mjpeg


def main() -> None:
    """Run different tests depending on the provided subcommand."""
    parser = argparse.ArgumentParser(
        prog="test_streamer",
        description="Test the camera preview streaming at varying levels of integration",
    )
    parser.set_defaults(func=main_help)
    subparsers = parser.add_subparsers()
    subparsers.add_parser("minimal").set_defaults(func=test_minimal)
    subparsers.add_parser("wrapped").set_defaults(func=test_wrapped)
    subparsers.add_parser("saving").set_defaults(func=test_saving)
    args = parser.parse_args()
    args.func()


def main_help() -> None:
    """Print a help message."""
    print("You must specify a subcommand! Re-run this command with the --help flag for details.")


def test_minimal() -> None:
    """Test the camera and MJPEG streamer without planktoscope-specific hardware abstractions."""
    loguru.logger.info("Starting minimal streaming test...")
    cam = picamera2.Picamera2()
    cam.configure(cam.create_video_configuration(main={"size": (640, 480)}))
    preview_stream = hardware.PreviewStream()
    server = mjpeg.StreamingServer(preview_stream, ("", 8000))

    try:
        cam.start_recording(encoders.MJPEGEncoder(), outputs.FileOutput(preview_stream))
        server.serve_forever()
    except KeyboardInterrupt:
        loguru.logger.info("Stopping...")
    finally:
        server.shutdown()
        server.server_close()
        cam.stop_recording()
        cam.close()


def test_wrapped() -> None:
    """Test the camera and MJPEG streamer with the basic thread-safe hardware abstraction."""
    loguru.logger.info("Starting wrapped streaming test...")
    preview_stream = hardware.PreviewStream()
    cam = hardware.PiCamera(preview_stream)
    server = mjpeg.StreamingServer(preview_stream, ("", 8000))

    try:
        cam.open()
        server.serve_forever()
    except KeyboardInterrupt:
        loguru.logger.info("Stopping...")
    finally:
        server.shutdown()
        server.server_close()
        cam.close()


def test_saving() -> None:
    """Test the camera and MJPEG streamer while saving images to the current directory."""
    loguru.logger.info("Starting saving streaming test...")
    preview_stream = hardware.PreviewStream()
    cam = hardware.PiCamera(preview_stream)
    server = mjpeg.StreamingServer(preview_stream, ("", 8000))

    try:
        cam.open()
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        while True:
            loguru.logger.info("Capturing frame...")
            cam.capture_file("test_preview_capture.jpg")
            time.sleep(1.0)
    except KeyboardInterrupt:
        loguru.logger.info("Stopping...")
    finally:
        server.shutdown()
        server_thread.join()
        server.server_close()
        cam.close()


if __name__ == "__main__":
    main()
