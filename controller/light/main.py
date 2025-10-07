import asyncio
import json

import aiomqtt
import sys
import signal

import helpers

from . import MCP4725 as led


client = None
loop = asyncio.new_event_loop()


async def start() -> None:
    if (await helpers.get_hat_version()) != 3.3:
        sys.exit()

    led.init()
    global client
    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)
    async with client:
        _ = await asyncio.gather(
            client.subscribe("light"),
            publish_status(),
        )
        async for message in client.messages:
            await handle_message(message)


async def handle_message(message) -> None:
    if not message.topic.matches("light"):
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
    elif action == "save":
        if hasattr(led, 'save')
            led.save()

async def on() -> None:
    led.on()
    await publish_status()


async def off() -> None:
    led.off()
    await publish_status()


async def publish_status() -> None:
    payload = {"status": "Off" if led.is_on() else "On"}
    await client.publish(topic="status/light", payload=json.dumps(payload), retain=True)


async def stop() -> None:
    await off()
    led.deinit()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
