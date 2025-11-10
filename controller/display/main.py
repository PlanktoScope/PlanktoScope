import asyncio
import json
import signal
import sys

import aiomqtt  # type: ignore

import helpers

client = None
loop = asyncio.new_event_loop()


async def start() -> None:
    # There is no display on PlanktoScope HAT < 3.3
    if (await helpers.get_hat_version()) != 3.3:
        sys.exit()

    print("cool")

    global client
    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)
    async with client:
        await client.subscribe("display")
        # _ = await asyncio.gather(
        #     client.subscribe("display"),
        #     publish_status(),
        # )
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
    # elif action == "save":
    #     if hasattr(bubbler, "save"):
    #         bubbler.save()


async def on() -> None:
    print("on")
    # await publish_status()


async def off() -> None:
    print("off")
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
