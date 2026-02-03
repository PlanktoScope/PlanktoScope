import json
import socket

import aiofiles
import aiomqtt
import paho


async def get_hat_version() -> float | None:
    try:
        async with aiofiles.open("/home/pi/PlanktoScope/hardware.json", mode="r") as file:
            hardware = json.loads(await file.read())
            hat_version = hardware.get("hat_version")
            if hat_version is None:
                return None
            else:
                return float(hat_version)
    except FileNotFoundError:
        return None


async def mqtt_reply(client: aiomqtt.Client, message: aiomqtt.Message) -> None:
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


def get_machine_name():
    hostname = socket.gethostname()
    return hostname.removeprefix("planktoscope-")
