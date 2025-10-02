import asyncio
import json

from loguru import logger
import aiomqtt  # type: ignore
import gpiozero  # type: ignore
import paho

# pymon "poetry run python -u planktoscopehat/bubbler.py" -x

device = gpiozero.DigitalOutputDevice(19)
client = None


async def main() -> None:
    global client
    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)
    async with client:
        await client.subscribe("actuator/bubbler")
        await publish_status()
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


def exit() -> None:
    device.close()


if __name__ == "__main__":
    try:
        loop = asyncio.run(main())
    except KeyboardInterrupt:
        exit()

# TODO:
# turn off bubbler on exit
# publish status on exit
