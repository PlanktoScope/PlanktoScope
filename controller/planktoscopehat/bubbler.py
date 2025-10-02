import asyncio
import json

# import threading
import multiprocessing

# import time
# from typing import override
from loguru import logger
import aiomqtt  # type: ignore
import gpiozero  # type: ignore
import paho
import functools
import os
import signal

device = gpiozero.DigitalOutputDevice(19)

# pymon "poetry run python -u planktoscopehat/bubbler.py" -x


class Worker(multiprocessing.Process):
    def __init__(self, event, configuration) -> None:
        super().__init__(name="bubbler")
        self.stop_event = event

    def exit(self, signame, loop) -> None:
        # print("got signal %s: exit" % signame)
        device.close()
        loop.stop()

    def run(self) -> None:
        loop = asyncio.get_event_loop()

        for signame in {"SIGINT", "SIGTERM"}:
            loop.add_signal_handler(
                getattr(signal, signame), functools.partial(self.exit, signame, loop)
            )

        loop.run_until_complete(self.main())

    async def handle_message(self, message) -> None:
        if not message.topic.matches("actuator/bubbler"):
            return

        payload = json.loads(message.payload.decode("utf-8"))
        action = payload.get("action")
        if action != None:
            await self.handle_action(action)

        response_topic = getattr(message.properties, "ResponseTopic", None)
        if response_topic is None:
            return

        correlation_data = getattr(message.properties, "CorrelationData", None)
        properties = paho.mqtt.properties.Properties(paho.mqtt.packettypes.PacketTypes.PUBLISH)

        if correlation_data is not None:
            properties.CorrelationData = correlation_data

        await self.client.publish(
            topic=response_topic, payload=json.dumps({}), qos=1, properties=properties, retain=False
        )

    async def handle_action(self, action: str) -> None:
        if action == "on":
            await self.on()
        elif action == "off":
            await self.off()

    async def on(self) -> None:
        device.on()
        await self.publish_status()

    async def off(self) -> None:
        device.off()
        await self.publish_status()

    async def publish_status(self) -> None:
        payload = {"status": "on" if device.value == 1 else "off"}
        await self.client.publish(topic="status/bubbler", payload=json.dumps(payload), retain=True)

    async def main(self) -> None:
        client = aiomqtt.Client(
            hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5
        )
        self.client = client
        async with client:
            await client.subscribe("actuator/bubbler")
            await self.publish_status()
            async for message in client.messages:
                await self.handle_message(message)


if __name__ == "__main__":
    bubbler_worker = Worker(None, None)
    bubbler_worker.start()
