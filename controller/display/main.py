import asyncio
import json
import os
import signal
import sys
import time

import aiomqtt  # type: ignore
from PIL import Image, ImageDraw, ImageFont  # type: ignore

import helpers

client = None
loop = asyncio.new_event_loop()

dirname = os.path.dirname(__file__)

# Configuration des chemins
picdir = os.path.join(dirname, "e-paper/pic")
libdir = os.path.join(dirname, "e-paper/lib")
if os.path.exists(libdir):
    sys.path.append(libdir)

epd = None
task = None
draw = None
font24 = None
image = None
epd2in9_V2 = None


def get_text_dimensions(text):
    assert draw is not None
    bbox = draw.textbbox((0, 0), text, font=font24)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


async def periodic():
    assert epd is not None
    assert draw is not None
    while True:
        current_time = time.strftime("%H:%M:%S")

        # Efface l'image (remplir en blanc)
        draw.rectangle((0, 0, epd.height, epd.width), fill=255)

        # Calculer taille du texte avec textbbox (Pillow 10+ friendly)
        bbox = draw.textbbox((0, 0), current_time, font=font24)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Centrer le texte
        x = (epd.height - text_w) // 2
        y = (epd.width - text_h) // 2

        # draw time
        draw.text((x, y), current_time, font=font24, fill=0)

        epd.display_Partial(epd.getbuffer(image))

        await asyncio.sleep(0.25)


async def configure(config):
    assert draw is not None
    assert epd is not None
    hostname = config["hostname"]
    ip = config["ip"]
    # serial_number = payload["serial_number"]
    # url = "http://" + hostname

    draw.text((5, 5), hostname, font=font24, fill=0)
    draw.text((epd.width - 5, epd.height - 5), ip, font=font24, fill=0)


async def start() -> None:
    # There is no display on PlanktoScope HAT < 3.3
    if (await helpers.get_hat_version()) != 3.3:
        sys.exit()

    global epd, draw, font24, image, epd2in9_V2
    from waveshare_epd import epd2in9_V2  # type: ignore

    epd = epd2in9_V2.EPD()
    epd.init()
    epd.Clear(0xFF)

    font24 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 24)

    image = Image.new("1", (epd.height, epd.width), 255)  # Mode 1-bit, fond blanc
    draw = ImageDraw.Draw(image)

    global client
    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)
    async with client:
        # await client.subscribe("display")
        _ = await asyncio.gather(
            client.subscribe("display"),
            on(),
        )
        async for message in client.messages:
            await handle_message(message)


async def handle_message(message) -> None:
    if not message.topic.matches("display"):
        return

    payload = json.loads(message.payload.decode("utf-8"))
    action = payload.get("action")
    if action is not None:
        await handle_action(action, payload)

    await helpers.mqtt_reply(client, message)


async def handle_action(action: str, payload) -> None:
    if action == "on":
        await on()
    elif action == "off":
        await off()
    elif action == "configure" and "config" in payload:
        await configure(payload["config"])
    # elif action == "save":
    #     if hasattr(bubbler, "save"):
    #         bubbler.save()


async def on() -> None:
    global task
    if task is not None:
        return
    task = loop.create_task(periodic())
    # await publish_status()


async def off() -> None:
    if task is not None:
        task.cancel()
    if epd is not None:
        epd.Clear(0xFF)
    if (epd2in9_V2) is not None:
        epd2in9_V2.epdconfig.module_exit()
    # await publish_status()


# async def publish_status() -> None:
#     assert bubbler is not None
#     assert client is not None
#     payload = {"status": "Off" if bubbler.is_off() else "On"}
#     await client.publish(topic="actuator/bubbler", payload=json.dumps(payload), retain=True)


async def stop() -> None:
    await off()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
