import asyncio
import json

import aiomqtt
import gpiozero
import paho
import sys
import signal

import helpers

# pymon "uv run planktoscopehat/bubbler.py" -x

device = gpiozero.DigitalOutputDevice(19)
client = None
loop = asyncio.new_event_loop()


async def start() -> None:
    # There is no GPIO bubbler on PlanktoScope HAT < 3.3
    # only USB powered bubbler
    if (await helpers.get_hat_version()) != 3.3:
        sys.exit()

    device.value = 0
    global client
    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)
    async with client:
        _ = await asyncio.gather(
            client.subscribe("actuator/bubbler"),
            publish_status(),
        )
        async for message in client.messages:
            await handle_message(message)


async def handle_message(message) -> None:
    if not message.topic.matches("actuator/bubbler"):
        return

    payload = json.loads(message.payload.decode("utf-8"))
    action = payload.get("action")
    if action is not None:
        await handle_action(action)

    await helpers.mqtt_reply(client, message)


async def handle_action(action: str) -> None:
    if action == "on":
        await on()
    elif action == "off":
        await off()


async def on() -> None:
    device.on()
    await publish_status()


async def off() -> None:
    device.off()
    await publish_status()


async def publish_status() -> None:
    payload = {"status": "On" if device.value == 1 else "Off"}
    await client.publish(topic="status/bubbler", payload=json.dumps(payload), retain=True)


async def stop() -> None:
    await off()
    device.close()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
