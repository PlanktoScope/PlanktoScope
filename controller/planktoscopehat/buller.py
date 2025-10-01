import asyncio
import json

# import threading
import multiprocessing

# import time
# from typing import override
from loguru import logger
import aiomqtt  # type: ignore
import gpiozero  # type: ignore

device = gpiozero.DigitalOutputDevice(19)


class Worker(multiprocessing.Process):
    def __init__(
        self,
        # configuration: dict[str, typing.Any],
    ) -> None:
        super().__init__(name="buller")

    def run(self) -> None:
        asyncio.run(self.main())

    async def handle_message(self, message) -> None:
        if not message.topic.matches("actuator/buller"):
            return

        payload = json.loads(message.payload.decode("utf-8"))
        action = payload.get("action")
        if action != None:
            await self.handle_action(action)

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
        if device.value == 1:
            await self.publish({"status": "on"})
        else:
            await self.publish({"status": "off"})

    # private
    async def publish(self, payload) -> None:
        await self.client.publish("status/buller", json.dumps(payload))

    async def main(self) -> None:
        client = aiomqtt.Client(
            hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5
        )
        self.client = client
        async with client:
            await client.subscribe("actuator/buller")
            await self.publish_status()
            async for message in client.messages:
                await self.handle_message(message)


if __name__ == "__main__":
    buller_worker = Worker()
    buller_worker.start()
