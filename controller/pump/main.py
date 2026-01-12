import asyncio
import json
import signal
import time
from pprint import pprint

import aiofiles
import aiomqtt

import helpers
from motor.motor import Motor

"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2

# 507 steps per ml for PlanktoScope standard
# 5200 for custom NEMA14 pump with 0.8mm ID Tube
pump_steps_per_ml = 507
# pump max speed is in ml/min
pump_max_speed = 50

pump_started = False

pump_stepper = Motor(pin=23, spi_bus=0, spi_device=0)
pump_stepper.acceleration = 2000
pump_stepper.deceleration = pump_stepper.acceleration

client = None
loop = asyncio.new_event_loop()


async def start() -> None:
    global pump_steps_per_ml, pump_max_speed, client

    hardware_config = None
    try:
        async with aiofiles.open("/home/pi/PlanktoScope/hardware.json", mode="r") as file:
            hardware_config = json.loads(await file.read())
    except FileNotFoundError:
        return None

    if hardware_config is not None:
        # parse the config data. If the key is absent, we are using the default value
        pump_steps_per_ml = hardware_config.get("pump_steps_per_ml", pump_steps_per_ml)
        pump_max_speed = hardware_config.get("pump_max_speed", pump_max_speed)

    pump_stepper.speed = int(pump_max_speed * pump_steps_per_ml * 256 / 60)

    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)

    async with client:
        _ = await asyncio.gather(
            client.subscribe("actuator/pump"),
            # publish_status(),
        )
        async for message in client.messages:
            await handle_message(message)


async def handle_message(message) -> None:
    if not message.topic.matches("actuator/pump"):
        return

    payload = json.loads(message.payload.decode("utf-8"))
    pprint(payload)

    action = payload.get("action")
    if action is not None:
        await handle_action(action, payload)

    if client is not None:
        await helpers.mqtt_reply(client, message)


async def handle_action(action: str, payload) -> None:
    if action == "move":
        await startPump(payload)
    elif action == "stop":
        await stopPump()


async def startPump(payload) -> None:
    direction = None
    volume = None
    flowrate = None

    try:
        direction = payload["direction"]
        volume = int(payload["volume"])
        flowrate = int(payload["flowrate"])

    except Exception:
        # FIXME: add error handling
        return

    if flowrate == 0:
        # FIXME: add error handling
        return

    # await loop.run_in_executor(None, pump, direction, volume, flowrate)

    await pump(direction, volume, flowrate)


# The pump max speed will be at about 400 full steps per second
# This amounts to 0.9mL per seconds maximum, or 54mL/min
# NEMA14 pump with 3 rollers is 0.509 mL per round, actual calculation at
# Stepper is 200 steps/round, or 393steps/ml
# https://www.wolframalpha.com/input/?i=pi+*+%280.8mm%29%C2%B2+*+54mm+*+3
async def pump(direction, volume, flowrate=pump_max_speed):
    global pump_started

    """Moves the pump stepper

    Args:
        direction (string): direction of the pumping
        volume (int): volume to pump, in mL
        speed (int, optional): speed of pumping, in mL/min. Defaults to pump_max_speed.
    """

    # Validation of inputs
    if direction not in ["FORWARD", "BACKWARD"]:
        # FIXME: add error handling
        return

    # TMC5160 is configured for 256 microsteps
    nb_steps = round(pump_steps_per_ml * volume * 256, 0)
    if flowrate > pump_max_speed:
        flowrate = pump_max_speed
    steps_per_second = flowrate * pump_steps_per_ml * 256 / 60
    pump_stepper.speed = int(steps_per_second)

    await client.publish(
        topic="status/pump",
        payload=json.dumps({"status": "Started", "duration": nb_steps / steps_per_second}),
        retain=True,
    )

    await rotate(direction, nb_steps)

    await client.publish(
         topic="status/pump",
         payload=json.dumps({"status": "Done"}),
         retain=True
    )

def wait_at_goal():
    while True:
        if pump_stepper.at_goal():
            return
    time.sleep(0.01)

async def rotate(direction, nb_steps):
    if direction == "FORWARD":
        pump_started = True
        pump_stepper.go(FORWARD, nb_steps)
    elif direction == "BACKWARD":
        pump_started = True
        pump_stepper.go(BACKWARD, nb_steps)

    await asyncio.to_thread(wait_at_goal)

    pump_started = False
    pump_stepper.release()

async def stopPump() -> None:
    global pump_started
    pump_stepper.shutdown()
    pump_started = False
    if client is not None:
        await client.publish(
            topic="status/pump", payload=json.dumps({"status": "Interrupted"}), retain=True
        )


async def stop() -> None:
    await stopPump()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
