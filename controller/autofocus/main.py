"""Autofocus controller for PlanktoScope.

Uses Laplacian variance as a focus metric to find the optimal focus position
by sweeping through a range of positions and finding the sharpest image.

Usage:
    MQTT Topic: autofocus

    Actions:
        - {"action": "start"} - Start autofocus with default settings
        - {"action": "start", "range": 1000, "steps": 20} - Custom range (μm) and steps
        - {"action": "test"} - Capture current frame and report focus score
        - {"action": "stop"} - Stop autofocus in progress

    Status published to: status/autofocus
"""

import asyncio
import json
import signal
import time
from pprint import pprint

import aiomqtt
import cv2
import numpy as np

# Configuration
STREAM_URL = "rtsp://localhost:8554/cam"  # MJPEG stream URL
DEFAULT_RANGE_UM = 1000  # Total sweep range in micrometers
DEFAULT_STEPS = 20  # Number of steps in the sweep
SETTLE_TIME = 0.3  # Seconds to wait after focus movement before capturing
FOCUS_SPEED_MM_S = 1.0  # Focus movement speed in mm/s

client = None
loop = asyncio.new_event_loop()
autofocus_running = False
stop_requested = False


def calculate_laplacian_variance(image: np.ndarray) -> float:
    """Calculate Laplacian variance as a focus metric.

    Higher values indicate a sharper (more in-focus) image.

    Args:
        image: Input image (BGR or grayscale)

    Returns:
        Laplacian variance value
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    return float(variance)


def capture_frame_from_stream(url: str = STREAM_URL, timeout: float = 5.0) -> np.ndarray:
    """Capture a single frame from an MJPEG stream.

    Args:
        url: URL of the MJPEG stream
        timeout: Timeout in seconds

    Returns:
        Captured frame as numpy array

    Raises:
        RuntimeError: If frame capture fails
    """
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    start_time = time.time()
    frame = None

    try:
        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if ret and frame is not None:
                break
            time.sleep(0.1)
    finally:
        cap.release()

    if frame is None:
        raise RuntimeError(f"Failed to capture frame from {url}")

    return frame


def capture_frame_direct(device: int = 0) -> np.ndarray:
    """Capture a single frame directly from camera device.

    Args:
        device: Camera device index

    Returns:
        Captured frame as numpy array

    Raises:
        RuntimeError: If frame capture fails
    """
    cap = cv2.VideoCapture(device)

    try:
        ret, frame = cap.read()
        if not ret or frame is None:
            raise RuntimeError(f"Failed to capture frame from device {device}")
        return frame
    finally:
        cap.release()


async def capture_frame() -> np.ndarray:
    """Capture a frame, trying stream first then direct capture.

    Returns:
        Captured frame as numpy array
    """
    # Try MJPEG stream first
    try:
        return await asyncio.to_thread(capture_frame_from_stream)
    except Exception as e:
        print(f"Stream capture failed: {e}, trying direct capture...")

    # Fallback to direct camera
    return await asyncio.to_thread(capture_frame_direct)


async def move_focus_and_wait(distance_um: float, speed_mm_s: float = FOCUS_SPEED_MM_S) -> bool:
    """Move focus by a relative distance and wait for completion.

    Args:
        distance_um: Distance to move in micrometers (positive = UP/Near, negative = DOWN/Far)
        speed_mm_s: Movement speed in mm/s

    Returns:
        True if movement completed, False if interrupted
    """
    global client
    assert client is not None

    if abs(distance_um) < 1:
        return True

    direction = "UP" if distance_um > 0 else "DOWN"
    distance_mm = abs(distance_um) / 1000.0

    # Create event to wait for focus completion
    focus_done = asyncio.Event()
    focus_result = {"completed": False}

    async def wait_for_focus_done():
        """Wait for focus status to indicate completion."""
        async with aiomqtt.Client(hostname="localhost", port=1883) as status_client:
            await status_client.subscribe("status/focus")
            async for message in status_client.messages:
                try:
                    payload = json.loads(message.payload.decode("utf-8"))
                    if payload.get("status") in ["Done", "Interrupted"]:
                        focus_result["completed"] = payload.get("status") == "Done"
                        focus_done.set()
                        break
                except Exception:
                    pass

    # Start waiting for completion
    wait_task = asyncio.create_task(wait_for_focus_done())

    # Send move command
    payload = {
        "action": "move",
        "direction": direction,
        "distance": distance_mm,
        "speed": speed_mm_s
    }
    await client.publish(topic="actuator/focus", payload=json.dumps(payload))

    # Wait for completion with timeout
    try:
        expected_time = distance_mm / speed_mm_s + 1.0
        await asyncio.wait_for(focus_done.wait(), timeout=expected_time + 5.0)
    except asyncio.TimeoutError:
        print("Focus movement timed out")
        focus_result["completed"] = True  # Assume it moved anyway
    finally:
        wait_task.cancel()
        try:
            await wait_task
        except asyncio.CancelledError:
            pass

    # Let things settle
    await asyncio.sleep(SETTLE_TIME)

    return focus_result["completed"]


async def publish_status(status: dict) -> None:
    """Publish autofocus status to MQTT."""
    global client
    if client is not None:
        await client.publish(
            topic="status/autofocus",
            payload=json.dumps(status),
            retain=True
        )


async def autofocus(range_um: float = DEFAULT_RANGE_UM, steps: int = DEFAULT_STEPS) -> dict:
    """Perform autofocus sweep to find optimal focus position.

    Args:
        range_um: Total sweep range in micrometers
        steps: Number of measurement steps

    Returns:
        Dict with best_position, best_variance, and measurements
    """
    global autofocus_running, stop_requested

    autofocus_running = True
    stop_requested = False

    step_size = (2 * range_um) / steps  # Double range for both sides
    half_range = range_um  # Full range on each side of current position

    await publish_status({
        "status": "Starting",
        "range_um": range_um,
        "steps": steps
    })

    print(f"Starting autofocus: range={range_um}μm, steps={steps}")

    # Move to start of sweep (negative direction = DOWN/Far)
    print(f"Moving to start position: -{half_range}μm")
    await move_focus_and_wait(-half_range)

    if stop_requested:
        await publish_status({"status": "Stopped"})
        autofocus_running = False
        return {"status": "stopped"}

    best_variance = 0.0
    best_step = 0
    measurements = []

    for i in range(steps + 1):
        if stop_requested:
            await publish_status({"status": "Stopped"})
            autofocus_running = False
            return {"status": "stopped"}

        position = -half_range + (i * step_size)

        # Capture and measure
        try:
            frame = await capture_frame()
            variance = calculate_laplacian_variance(frame)
        except Exception as e:
            print(f"Error capturing frame at step {i}: {e}")
            variance = 0.0

        measurements.append({
            "step": i,
            "position_um": position,
            "variance": variance
        })

        print(f"Step {i}/{steps}: position={position:.1f}μm, variance={variance:.2f}")

        await publish_status({
            "status": "Sweeping",
            "step": i,
            "total_steps": steps,
            "position_um": position,
            "variance": variance
        })

        if variance > best_variance:
            best_variance = variance
            best_step = i

        # Move to next position (except on last step)
        if i < steps:
            await move_focus_and_wait(step_size)

    # Calculate position to move to best focus
    best_position = -half_range + (best_step * step_size)
    current_position = half_range  # We're at the end of the sweep
    move_to_best = best_position - current_position

    print(f"Best focus at step {best_step}, position={best_position:.1f}μm, variance={best_variance:.2f}")
    print(f"Moving {move_to_best:.1f}μm to best position")

    await publish_status({
        "status": "Moving to best",
        "best_step": best_step,
        "best_position_um": best_position,
        "best_variance": best_variance
    })

    # Move to best position
    await move_focus_and_wait(move_to_best)

    result = {
        "status": "Done",
        "best_step": best_step,
        "best_position_um": best_position,
        "best_variance": best_variance,
        "measurements": measurements
    }

    await publish_status(result)

    autofocus_running = False
    print("Autofocus complete!")

    return result


async def test_focus() -> dict:
    """Capture current frame and report focus score."""
    try:
        frame = await capture_frame()
        variance = calculate_laplacian_variance(frame)

        result = {
            "status": "Test",
            "variance": variance,
            "timestamp": time.time()
        }

        await publish_status(result)
        print(f"Current focus variance: {variance:.2f}")

        return result
    except Exception as e:
        error_result = {"status": "Error", "error": str(e)}
        await publish_status(error_result)
        return error_result


async def handle_message(message) -> None:
    """Handle incoming MQTT messages."""
    global autofocus_running, stop_requested

    if not message.topic.matches("autofocus"):
        return

    try:
        payload = json.loads(message.payload.decode("utf-8"))
        pprint(payload)

        action = payload.get("action")

        if action == "start":
            if autofocus_running:
                await publish_status({"status": "Busy", "message": "Autofocus already running"})
                return

            range_um = payload.get("range", DEFAULT_RANGE_UM)
            steps = payload.get("steps", DEFAULT_STEPS)

            # Run autofocus as a task so we can handle stop commands
            asyncio.create_task(autofocus(range_um, steps))

        elif action == "test":
            await test_focus()

        elif action == "stop":
            if autofocus_running:
                stop_requested = True
                await publish_status({"status": "Stopping"})
            else:
                await publish_status({"status": "Not running"})

    except Exception as e:
        print(f"Error handling message: {e}")
        await publish_status({"status": "Error", "error": str(e)})


async def start() -> None:
    """Start the autofocus controller."""
    global client

    print("Starting autofocus controller...")

    client = aiomqtt.Client(hostname="localhost", port=1883, protocol=aiomqtt.ProtocolVersion.V5)

    async with client:
        await client.subscribe("autofocus")

        await publish_status({"status": "Ready"})
        print("Autofocus controller ready, waiting for commands...")

        async for message in client.messages:
            await handle_message(message)


async def stop() -> None:
    """Stop the autofocus controller."""
    global stop_requested
    stop_requested = True
    loop.stop()


for s in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(s, lambda: asyncio.ensure_future(stop()))


def main():
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
