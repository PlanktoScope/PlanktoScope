import asyncio
import json

import aiomqtt
import sys
import signal

import helpers

from . import MCP4725 as bubbler

client = None
loop = asyncio.new_event_loop()


async def start() -> None:
    # There is no GPIO bubbler on PlanktoScope HAT < 3.3
    # only USB powered bubbler
    if (await helpers.get_hat_version()) != 3.3:
        sys.exit()

    bubbler.init()
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
        await handle_action(action, payload)

    await helpers.mqtt_reply(client, message)


async def handle_action(action: str, payload) -> None:
    if action == "on":
        await on()
    elif action == "off":
        await off()
    elif action == "settings":
        await handle_settings(payload)
    elif action == "save":
        if hasattr(bubbler, "save"):
            bubbler.save()


async def handle_settings(payload) -> None:
    if "current" in payload["settings"]:
        # {"settings":{"current":"20"}}
        current = payload["settings"]["current"]
        if bubbler.is_on():
            return
        bubbler.set_current(current)


async def on() -> None:
    bubbler.on()
    await publish_status()


async def off() -> None:
    bubbler.off()
    await publish_status()


async def publish_status() -> None:
    payload = {"status": "Off" if bubbler.is_off() else "On"}
    await client.publish(topic="actuator/bubbler", payload=json.dumps(payload), retain=True)


async def stop() -> None:
    await off()
    bubbler.deinit()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
