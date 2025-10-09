import asyncio
import json

import aiomqtt
import gpiozero
import sys
import signal

import helpers
from motor.motor import Motor

"""Step forward"""
FORWARD = 1
""""Step backward"""
BACKWARD = 2

pump_steps_per_ml = 2045
# pump max speed is in ml/min
pump_max_speed = 50

pump_started = False

pump_stepper = Motor(pin=23, spi_bus=0, spi_device=0)
pump_stepper.acceleration = 2000
pump_stepper.deceleration = pump_stepper.acceleration
pump_stepper.speed = int(pump_max_speed * pump_steps_per_ml * 256 / 60)

client = None
loop = asyncio.new_event_loop()


async def start() -> None:
    pump_stepper.shutdown()

    global client
    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)

    async with client:
        _ = await asyncio.gather(
            client.subscribe("actuator/pump"),
            # publish_status(),
        )
        async for message in client.messages:
            await handle_message(message)


async def handle_message(message) -> None:
    print(message)
    if not message.topic.matches("actuator/pump"):
        return

    payload = json.loads(message.payload.decode("utf-8"))
    action = payload.get("action")

    if action is not None:
        await handle_action(action, payload)

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

    await loop.run_in_executor(None, pump, direction, volume, flowrate)

    # pump(direction, volume, flowrate)


# The pump max speed will be at about 400 full steps per second
# This amounts to 0.9mL per seconds maximum, or 54mL/min
# NEMA14 pump with 3 rollers is 0.509 mL per round, actual calculation at
# Stepper is 200 steps/round, or 393steps/ml
# https://www.wolframalpha.com/input/?i=pi+*+%280.8mm%29%C2%B2+*+54mm+*+3
def pump(direction, volume, flowrate=pump_max_speed):
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

    # await client.publish(
    #     topic="status/pump",
    #     payload=json.dumps({"status": "Started", "duration": nb_steps / steps_per_second}),
    #     retain=True,
    # )

    # Depending on direction, select the right direction for the pump
    if direction == "FORWARD":
        pump_started = True
        pump_stepper.go(FORWARD, nb_steps)
    elif direction == "BACKWARD":
        pump_started = True
        pump_stepper.go(BACKWARD, nb_steps)

    while pump_started:
        if pump_stepper.at_goal():
            # await client.publish(
            #     topic="status/pump",
            #     payload=json.dumps({"status": "Done"}),
            #     retain=True,
            # )
            pump_started = False
            pump_stepper.shutdown()
            break


async def stopPump() -> None:
    global pump_started
    pump_stepper.shutdown()
    pump_started = False
    await client.publish(
        topic="status/pump", payload=json.dumps({"status": "Interrupted"}), retain=True
    )


# async def publish_status() -> None:
#     payload = {"status": "On" if device.value == 1 else "Off"}
#     await client.publish(topic="status/bubbler", payload=json.dumps(payload), retain=True)


async def stop() -> None:
    await stopPump()
    # device.close()
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
