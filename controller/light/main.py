import asyncio
import json

import aiomqtt
import paho
import sys
import signal

import board  # type: ignore
import busio  # type: ignore
from adafruit_mcp4725 import MCP4725  # type: ignore

import helpers

MCP4725_ADDR = 0x60
# Proportional 0 to 5V
VALUE_MIN = 0
VALUE_MAX = 65535
VOLTAGE_MIN = 0
# if you run it from 3.3V, the output range is 0-3.3V. If you run it from 5V the output range is 0-5V.
VOLTAGE_MAX = 5

client = None
loop = asyncio.new_event_loop()
i2c = busio.I2C(board.SCL, board.SDA)
dac = MCP4725(i2c, address=MCP4725_ADDR)


def map_to_voltage(value):
    return (value / VALUE_MAX) * VOLTAGE_MAX


def map_to_adc(voltage):
    return int((voltage / VOLTAGE_MAX) * VALUE_MAX)


async def start() -> None:
    if (await helpers.get_hat_version()) != 3.3:
        sys.exit()

    dac.value = 0
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
        dac.save_to_eeprom()


async def on() -> None:
    dac.value = VALUE_MAX
    await publish_status()


async def off() -> None:
    dac.value = VALUE_MIN
    await publish_status()


async def publish_status() -> None:
    payload = {"status": "Off" if dac.value == 0 else "On"}
    await client.publish(topic="status/light", payload=json.dumps(payload), retain=True)


async def stop() -> None:
    await off()
    i2c.deinit()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
