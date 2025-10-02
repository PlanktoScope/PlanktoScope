import asyncio
import json

import aiomqtt
import gpiozero
import paho
import sys
import signal
import aiofiles

import identity

# pymon "poetry run python -u planktoscopehat/bubbler.py" -x

device = gpiozero.DigitalOutputDevice(19)
client = None
loop = asyncio.new_event_loop()


async def start() -> None:
    if await identity.get_hat_version() != 3.2:
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
    if action != None:
        await handle_action(action)

    response_topic = getattr(message.properties, "ResponseTopic", None)
    if response_topic is None:
        return

    correlation_data = getattr(message.properties, "CorrelationData", None)
    properties = paho.mqtt.properties.Properties(paho.mqtt.packettypes.PacketTypes.PUBLISH)

    if correlation_data is not None:
        properties.CorrelationData = correlation_data

    await client.publish(
        topic=response_topic, payload=json.dumps({}), qos=1, properties=properties, retain=False
    )


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
    payload = {"status": "on" if device.value == 1 else "off"}
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
