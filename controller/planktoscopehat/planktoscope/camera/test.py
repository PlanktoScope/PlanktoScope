import time
from pprint import *
import typing

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import PyavOutput

picam2 = Picamera2()
pprint(picam2.sensor_modes)

# High framerate
config_preview = picam2.create_preview_configuration(main={}, lores={})

# High everything?
config_video = picam2.create_video_configuration(main={}, lores={})

# High quality
config_still = picam2.create_still_configuration(
    main={},
    lores={"size": (800, 600)},
    buffer_count=3,
    queue=False
)

# picam2.configure(config_video)
picam2.configure(config_still)


# main = {'size': (1920, 1080), 'format': 'YUV420'}
# controls = {'FrameRate': 30}
# video_config = picam2.create_video_configuration(main, controls=controls)
# picam2.configure(video_config)
encoder = H264Encoder(bitrate=10000000)
# http://pkscope-sponge-care-280-1:8889/cam/
output = PyavOutput("rtsp://127.0.0.1:8554/cam", format="rtsp")
print("Camera starting")
picam2.start_recording(encoder=encoder, output=output, name="lores")


time.sleep(2)

print('capture')

# picam2.switch_mode(config_still)

request = picam2.capture_request()

# https://github.com/raspberrypi/picamera2/blob/63f3be10e317c4b4b0a93e357d7db18fe098e9d4/picamera2/request.py#L213
request.save(name="main", file_output="main.jpeg")
request.save(name="lores", file_output="lores.jpeg")

# https://github.com/raspberrypi/picamera2/blob/63f3be10e317c4b4b0a93e357d7db18fe098e9d4/picamera2/request.py#L263
request.save_dng(name="raw", file_output="raw.dng")

# https://github.com/raspberrypi/picamera2/blob/63f3be10e317c4b4b0a93e357d7db18fe098e9d4/picamera2/request.py#L154
metadata = request.get_metadata()
pprint(metadata)

request.release()

print('done')

# capture_size =
# preview_size
# buffer_count
# queue

# main_config: dict[str, typing.Any] = {}
# # if (main_size := self._stream_config.capture_size) is not None:
# #     main_config["size"] = main_size
# lores_config: dict[str, typing.Any] = {}
# # if (lores_size := self._stream_config.preview_size) is not None:
# #     lores_config["size"] = lores_size
# # Note(ethanjli): we use the `create_still_configuration` to get the best defaults for still
# # images from the "main" stream:
# config2 = picam2.create_still_configuration(
#     main_config,
#     lores_config,
#     buffer_count=3,
#     # queue=self._stream_config.queue,
# )
# picam2.configure(config2)
#

# still_config = picam2.create_still_configuration(buffer_count=2)


# request = picam2.capture_request()
# request.save("main", 'wow.jpeg')  # pylint: disable=no-member
# print(request.get_metadata())
# request.release()  # pylint: disable=no-member

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Camera stopping")
