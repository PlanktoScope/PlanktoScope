import json
import aiofiles
import paho
import aiomqtt


async def get_hat_version() -> float | None:
    async with aiofiles.open("/home/pi/PlanktoScope/hardware.json", mode="r") as file:
        hardware = json.loads(await file.read())
        hat_version = hardware.get("hat_version")
        if hat_version is None:
            return None
        else:
            return float(hat_version)


async def get_hat_type() -> str:
    async with aiofiles.open("/home/pi/PlanktoScope/hardware.json", mode="r") as file:
        hardware = json.loads(await file.read())
        hat_type = hardware.get("hat_type")
        if hat_type is not None:
            return hat_type

    async with aiofiles.open("/home/pi/PlanktoScope/config.json", mode="r") as file:
        config = json.loads(await file.read())
        if config["acq_instrument"] == "PlanktoScope v2.1":
            return "adafruit"
        else:
            return "planktoscope"


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
