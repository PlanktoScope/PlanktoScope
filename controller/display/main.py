import asyncio
import json
import logging
import os
import signal
import sys
from pprint import pprint

import aiomqtt  # type: ignore
from PIL import Image, ImageDraw, ImageFont  # type: ignore

import helpers
from identity import load_machine_name

# Hardware
# We use Waveshare 2.9inch E-Ink display module (black and white) SPI
# https://www.waveshare.com/2.9inch-e-paper-module.htm
# https://www.waveshare.com/wiki/2.9inch_e-Paper_Module

# Software
# We use the Python implementation provided by Waveshare
# https://github.com/waveshareteam/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd
# As well as Pillow to draw the image rendered to the screen
# https://pillow.readthedocs.io/en/stable/index.html
# https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
# https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html

logging.basicConfig(level=logging.DEBUG)

client = None
loop = asyncio.new_event_loop()

dirname = os.path.dirname(__file__)
picdir = os.path.join(dirname, "e-paper/pic")
libdir = os.path.join(dirname, "e-paper/lib")
if os.path.exists(libdir):
    sys.path.append(libdir)

epd = None
fontsmall = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 18)
fontnormal = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 24)
fontbig = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 28)
image = None
draw = None
epd2in9_V2 = None
machine_name = load_machine_name()

width = None
height = None


def drawURL(draw, url):
    x = 0
    y = 0
    draw.text((x, y), text=url, font=fontnormal, fill=0)


def drawMachineName(draw, machine_name):
    assert width is not None
    assert height is not None
    x = width // 2
    y = height // 2
    draw.text((x, y), text=machine_name, anchor="mm", font=fontbig, fill=0)


def drawBrand(draw):
    text = "FairScope"
    x = width
    y = height
    draw.text((x, y), text=text, anchor="rd", font=fontsmall, fill=0)


def render(
    url="",
):
    assert epd is not None
    assert width is not None
    assert height is not None

    global image, draw
    if image is None or draw is None:
        image = Image.new("1", (epd.height, epd.width), 255)
        draw = ImageDraw.Draw(image)

    # clear screen
    # # TODO: only clear relevant area ?
    draw.rectangle((0, 0, height, width), fill=255)

    # center
    drawMachineName(draw, machine_name)
    # top left
    drawURL(draw, url)
    # bottom right
    drawBrand(draw)

    epd.display_Partial(epd.getbuffer(image))


async def configure(config):
    url = config.get("url", "")
    render(url)


async def clear():
    assert epd is not None
    assert width is not None
    assert height is not None
    # not functional
    # epd.Clear(0xFF)
    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, height, width), fill=255)
    epd.display_Partial(epd.getbuffer(image))


async def start() -> None:
    # There is no display on PlanktoScope HAT < 3.3
    if (await helpers.get_hat_version()) != 3.3:
        sys.exit()

    global epd, epd2in9_V2, width, height
    from waveshare_epd import epd2in9_V2  # type: ignore

    epd = epd2in9_V2.EPD()
    epd.init()
    epd.Clear(0xFF)
    # horizontal
    width = epd.height
    height = epd.width

    render(url="192.168.4.1")

    global client
    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)
    task_group = asyncio.TaskGroup()
    async with client, task_group:
        _ = await asyncio.gather(
            client.subscribe("display"),
        )
        async for message in client.messages:
            task_group.create_task(handle_message(message))


async def handle_message(message) -> None:
    if not message.topic.matches("display"):
        return

    payload = json.loads(message.payload.decode("utf-8"))
    pprint(payload)

    action = payload.get("action")
    if action is not None:
        await handle_action(action, payload)

    if client is not None:
        await helpers.mqtt_reply(client, message)


async def handle_action(action: str, payload) -> None:
    if action == "clear":
        await clear()
    if action == "configure" and "config" in payload:
        await configure(payload["config"])


async def stop() -> None:
    if epd is not None:
        epd.Clear(0xFF)
    if (epd2in9_V2) is not None:
        epd2in9_V2.epdconfig.module_exit()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
