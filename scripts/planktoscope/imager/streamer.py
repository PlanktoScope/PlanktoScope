from loguru import logger

import time

import socketserver
import http.server


################################################################################
# Classes for the PiCamera Streaming
################################################################################
class StreamingHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, delay, *args, **kwargs):
        self.delay = delay
        super(StreamingHandler, self).__init__(*args, **kwargs)

    @logger.catch
    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/stream.mjpg")
            self.end_headers()
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
                        with open("/dev/shm/mjpeg/cam.jpg", "rb") as jpeg:  # nosec
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
