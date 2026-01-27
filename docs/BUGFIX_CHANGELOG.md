# Bug Fix Change Log

This document tracks bug fixes made to the PlanktoScope Update Dashboard branch.
Each fix includes the original code so changes can be reverted if needed.

---

## Fix #1: H.264 Video Stream Corruption (RPi5)

**Date:** 2026-01-23
**File:** `controller/camera/hardware.py`
**Lines:** 21, 287-301
**Issue:** Severe video corruption/pixelization in live stream on Raspberry Pi 5

### Problem Description

The video stream displayed severe H.264 decoding artifacts on RPi5 - blocky, pixelated corruption affecting the entire frame. This has been present since the beginning on RPi5.

**Root Cause:** The RPi5 preview resolution `2028x1520` is NOT 16-pixel aligned
- 2028 / 16 = 126.75 
- H.264 requires 16-pixel macroblock alignment
- The code comment on line 17 mentions this: "anything <= 1920x1080 divisible by 16 (required by H.264 macroblock alignment)"

The RPi4 resolution (1440x1080) is properly aligned, which is why it works there.

### Screenshot of Issue

See: `/Users/adam/Documents/Update_dashboard/divx.jpg`

### Part A: Resolution Fix (Line 21)

**Original Code:**
```python
preview_size = (1440, 1080) if (get_platform() == Platform.VC4) else (2028, 1520)
```

**New Code:**
```python
preview_size = (1440, 1080) if (get_platform() == Platform.VC4) else (1920, 1440)
```

**Why 1920x1440:**
- 1920 / 16 = 120 (aligned!)
- 1440 / 16 = 90 (aligned!)
- Maintains 4:3 aspect ratio
- Well-supported, commonly used resolution

### Part B: Encoder Settings (Lines 287-301)

Also added encoder improvements for network resilience:

**Original Code:**
```python
        encoder = encoders.H264Encoder(
            # picamera2-manual.pdf 7.1.1. H264Encoder
            # the bitrate (in bits per second) to use. The default value None will cause the encoder to
            # choose an appropriate bitrate according to the Quality when it starts.
            # bitrate=None,
            # picamera2-manual.pdf 7.1.1. H264Encoder
            # whether to repeat the stream's sequence headers with every Intra frame (I-frame). This can
            # be sometimes be useful when streaming video over a network, when the client may not receive the start of the
            # stream where the sequence headers would normally be located.
            # repeat=False,
            # picamera2-manual.pdf 7.1.1. H264Encoder
            # iperiod (default None) - the number of frames from one I-frame to the next. The value None leaves this at the
            # discretion of the hardware, which defaults to 60 frames.
            # iperiod=None
        )
```

**New Code:**
```python
        encoder = encoders.H264Encoder(
            # FIX: Use baseline profile to disable B-frames (WebRTC doesn't support B-frames)
            # See: https://github.com/bluenviron/mediamtx/issues/3022
            # See: https://github.com/raspberrypi/picamera2/issues/785
            profile="baseline",
            # picamera2-manual.pdf 7.1.1. H264Encoder
            # whether to repeat the stream's sequence headers with every Intra frame (I-frame). This can
            # sometimes be useful when streaming video over a network, when the client may not receive the start of the
            # stream where the sequence headers would normally be located.
            repeat=True,  # FIX: Repeat headers for network resilience
            # picamera2-manual.pdf 7.1.1. H264Encoder
            # iperiod (default None) - the number of frames from one I-frame to the next. The value None leaves this at the
            # discretion of the hardware, which defaults to 60 frames.
            iperiod=15,  # FIX: I-frame every 15 frames for faster recovery
        )
```

### Part C: MediaMTX Buffer Fix

**File:** `os/mediamtx/mediamtx.yml`

Added `writeQueueSize: 1024` to prevent packet drops on RPi5 software encoder.

**Original:** (no writeQueueSize setting)

**New:**
```yaml
writeQueueSize: 1024
```

### Research Notes

- **Root cause:** WebRTC doesn't support H.264 B-frames, causing stream corruption
- **Solution:** Use `profile="baseline"` which disables B-frames
- **References:**
  - [MediaMTX B-frames issue](https://github.com/bluenviron/mediamtx/issues/3022)
  - [picamera2 baseline profile](https://github.com/raspberrypi/picamera2/issues/785)
  - [picamera2 RPi5 H264 issues](https://github.com/raspberrypi/picamera2/issues/1135)

**Note:** Explicit bitrate (8 Mbps) and iperiod=1 were tried but made things worse.

### How to Revert

**Part A (Resolution):** Change line 21 back to:
```python
preview_size = (1440, 1080) if (get_platform() == Platform.VC4) else (2028, 1520)
```

**Part B (Encoder):** Remove `profile="baseline"`, `repeat=True`, and `iperiod=15` parameters from H264Encoder().

**Part C (MediaMTX):** Remove `writeQueueSize: 1024` from mediamtx.yml.

### Expected Outcome

- Resolution alignment (16-pixel) eliminates macroblock alignment corruption
- `profile="baseline"` disables B-frames which WebRTC cannot decode
- `repeat=True` provides header resilience for network issues
- `iperiod=15` provides reasonable keyframe frequency
- `writeQueueSize: 1024` prevents packet drops from buffer overflow

---

## Fix #2: Calibration Settings Not Persisting

**Date:** 2026-01-23
**File:** `node-red/settings.cjs`
**Lines:** 341-345
**Issue:** Calibration settings reset on system restart

### Problem Description

Node-RED context storage uses `localfilesystem` module which flushes to disk every 30 seconds by default. If Node-RED restarts before flush completes, calibration data is lost.

### Original Code (for revert)

```javascript
    contextStorage: {
       default: {
           module:"localfilesystem"
       },
    },
```

### New Code

```javascript
    contextStorage: {
       default: {
           module: "localfilesystem",
           config: {
               flushInterval: 5,  // FIX: Flush every 5 seconds instead of default 30 to prevent calibration data loss on restart
           }
       },
    },
```

### How to Revert

Remove the `config` object with `flushInterval` from the contextStorage setting.

### Expected Outcome

- Calibration settings will be saved to disk every 5 seconds instead of 30
- Much less likely to lose data on restart
- Trade-off: Slightly more disk I/O (negligible impact)

### Calibration Data Stored

The following global context variables are persisted:
- `calibration_pixel_size` - pixel size in µm/pixel
- `calibration_scale_factor`, `calibration_sensor_width`, `calibration_stream_width`
- `calibration_known_distance`, `calibration_measured_distance`
- `calibration_markerA_x`, `calibration_markerA_y`, `calibration_markerB_x`, `calibration_markerB_y`
- `calibration_wbg_red`, `calibration_wbg_blue` - white balance gains
- `calibration_nb_step` - pump steps per mL

**Status:** Applied and deployed to PlanktoScope (2026-01-24)
**Deployment:** `scp node-red/settings.cjs` to `/home/pi/PlanktoScope/node-red/settings.cjs`
**Service restart required:** `sudo systemctl restart nodered`

---

## Enhancement #1: Segmentation Mask Cyan Opacity Effect

**Date:** 2026-01-23
**Files:**
- `frontend/src/pages/preview/SegmentationOverlay.jsx`
- `frontend/src/pages/preview/segmentation/index.jsx`
- `frontend/src/pages/preview/index.jsx`

**Issue:** Segmentation masks used varying hue colors and 50% opacity, making them less visually appealing

### Problem Description

The segmentation mask overlays used a rainbow of colors based on object index (`hsl(index * 137.5, 70%, 50%)`) with 50% opacity. This was inconsistent and didn't highlight detected objects as clearly.

### Original Code (for revert)

```javascript
const hue = (index * 137.5) % 360
const color = `hsl(${hue}, 70%, 50%)`
// ...
ctx.globalAlpha = 0.5
```

### New Code

```javascript
// Cyan color for segmentation overlay (matching the cool opacity effect Thibaut likes)
const maskColor = "rgb(0, 220, 220)"  // Cyan fill color
const bboxColor = "rgb(0, 128, 128)"  // Darker teal for bounding box
// ...
ctx.globalAlpha = 0.35  // Subtle transparency to see underlying image
```

### How to Revert

Replace the `maskColor` and `bboxColor` constants with the original hue-based color generation, and change `globalAlpha` back to `0.5`.

### Expected Outcome

- Consistent cyan/teal color scheme for all detected objects
- Subtle 35% opacity allows underlying image details to show through
- Darker teal bounding box provides clear boundary without being harsh
- Matches the professional microscopy overlay aesthetic

**Status:** Applied

---

## Enhancement #2: Blur Metric Visualization on Segmentation Page

**Date:** 2026-01-24
**Files:**
- `frontend/src/pages/preview/segmentation/index.jsx`
- `frontend/src/pages/preview/segmentation/styles.module.css`

**Issue:** Need blur visualization (sparkline + heatmap) for focus quality monitoring during live segmentation

### Changes Made

**Part A: Added blur state and visualization to `segmentation/index.jsx`:**
- Added `blurHistory` state for sparkline (last 60 values)
- Added `blurGrid` state for heatmap data
- Added `showHeatmap` toggle state
- Added `blurStats()` computed function for min/avg/max
- Added `sparklinePath()` function for SVG rendering
- Added `drawHeatmap()` function for heatmap canvas
- Added `toggleHeatmap()` and `clearHeatmap()` helper functions
- Updated message handler to capture `blur_grid` from MQTT
- Replaced simple focus indicator with full blur panel UI
- Added heatmap canvas overlay to image wrapper

**Part B: Added CSS styles to `segmentation/styles.module.css`:**
- `.blur_panel` - container for blur visualization
- `.blur_value` - numeric focus value display
- `.sparkline_container` / `.sparkline` - SVG sparkline styling
- `.blur_stats` - min/avg/max display
- `.heatmap_btn` / `.heatmap_active` - toggle button
- `.heatmap_canvas` - heatmap overlay positioning

### How to Revert

**Part A:** Remove the following from `segmentation/index.jsx`:
- `BLUR_HISTORY_SIZE` constant
- `blurHistory`, `blurGrid`, `showHeatmap` state signals
- `heatmapCanvasRef` ref
- `blurStats()`, `sparklinePath()`, `drawHeatmap()`, `clearHeatmap()`, `toggleHeatmap()` functions
- Blur-related message handler updates (setBlurHistory, setBlurGrid)
- Reset statements in handleToggle (setBlurHistory, setBlurGrid)
- Replace the `blur_panel` div with original focus indicator:
```jsx
<div class={styles.focus_indicator}>
  <span class={styles.stat_label}>Focus</span>
  <span class={styles.focus_status} style={{ color: focusStatus().color }}>
    <span class={styles.focus_icon}>{focusStatus().icon}</span>
    {focusStatus().label}
  </span>
</div>
```
- Remove heatmap canvas from image wrapper, restore to:
```jsx
<canvas ref={canvasRef} class={styles.overlay_canvas} />
```

**Part B:** Remove CSS classes from `.blur_panel` through `.heatmap_canvas` from `styles.module.css`

### Expected Outcome

- Real-time sparkline showing blur trend over last 60 frames
- Numeric blur value with color coding (red < 25, yellow 25-50, green > 50)
- Min/avg/max statistics displayed compactly
- Toggleable heatmap overlay showing regional blur, still needs work (red=blurry, green=sharp)

### Note on Previous Issue

An earlier attempt to add this to `preview/index.jsx` caused pump control issues (pump wouldn't stop). The issue was likely caused by using `createEffect` with refs. This implementation avoids that by drawing heatmap directly in `onImageLoad` callback.

**Status:** Applied and deployed to PlanktoScope (2026-01-24)
**Deployment:** `scp -r frontend/dist/* pi@planktoscope-butter-earth.local:/home/pi/PlanktoScope/frontend/dist/`

---

## Fix #3: Video Stream Not Working Over WiFi Hotspot

**Date:** 2026-01-25
**File:** `/usr/local/etc/mediamtx.yml` (on device), `os/mediamtx/mediamtx.yml` (in repo)
**Issue:** Video streams work over ethernet but fail when connected via WiFi hotspot

### Problem Description

When connecting to the PlanktoScope via WiFi hotspot (192.168.4.1), the UI loads correctly but the video stream does not display. The same stream works perfectly when connected via ethernet (10.0.0.160).

**Symptoms:**
- UI accessible at http://192.168.4.1
- Video stream never loads (blank/spinning)
- No errors in browser console (connection just hangs)
- Stream works fine over ethernet

### Root Cause Analysis

**Finding:** WebRTC ICE candidate gathering fails on hotspot network due to unreachable STUN servers.

The MediaMTX configuration relied on public STUN servers for WebRTC ICE candidate discovery:
```yaml
webrtcICEServers2:
  - url: stun:stun.cloudflare.com:3478
  - url: stun:stun.services.mozilla.com:3478
  - url: stun:stun.fbsbx.com:3478
```

When connected via hotspot:
1. The hotspot network (192.168.4.0/24) typically has no internet access
2. WebRTC tries to reach STUN servers to gather ICE candidates
3. STUN servers are unreachable → ICE gathering times out
4. WebRTC connection never establishes
5. Video stream fails

Over ethernet, the RPi has internet access, so STUN works and streaming succeeds.

### Diagnostic Commands Used

```bash
# Confirmed MediaMTX listening on all interfaces
ss -tlnp | grep 8889
# Output: LISTEN 0 4096 *:8889 *:*

# Confirmed HTTP endpoint accessible on hotspot IP
curl -v http://192.168.4.1:8889/cam/
# Output: HTTP/1.1 200 OK

# Confirmed both interfaces active
ip addr show wlan0  # 192.168.4.1/24
ip addr show eth0   # 10.0.0.160/24
```

### Original Code (for revert)

```yaml
# https://github.com/bluenviron/mediamtx/blob/v1.15.6/mediamtx.yml

# https://mediamtx.org/docs/usage/webrtc-specific-features#solving-webrtc-connectivity-issues
# webrtcAdditionalHosts:
#   [
#     localhost,
#     planktoscope.local,
#     pkscope.local,
#     192.168.4.1,
#     planktoscope-sponge-care,
#     planktoscope-sponge-care.local,
#     home.pkscope,
#   ]

# ICE servers...
webrtcICEServers2:
  - url: stun:stun.cloudflare.com:3478
  - url: stun:stun.services.mozilla.com:3478
  - url: stun:stun.fbsbx.com:3478
```

### New Code

```yaml
# https://github.com/bluenviron/mediamtx/blob/v1.15.6/mediamtx.yml

# https://mediamtx.org/docs/usage/webrtc-specific-features#solving-webrtc-connectivity-issues
# FIX: Enable webrtcAdditionalHosts for local network streaming without STUN dependency
webrtcAdditionalHosts:
  - localhost
  - planktoscope.local
  - pkscope.local
  - 192.168.4.1
  - 10.0.0.160
  - planktoscope-butter-earth
  - planktoscope-butter-earth.local
  - home.pkscope

# ICE servers. Needed only when local listeners can't be reached by clients.
# STUN servers allows to obtain and share the public IP of the server.
# TURN/TURNS servers forces all traffic through them.
webrtcICEServers2:
  - url: stun:stun.cloudflare.com:3478
  - url: stun:stun.services.mozilla.com:3478
  - url: stun:stun.fbsbx.com:3478
```

### How the Fix Works

The `webrtcAdditionalHosts` setting tells MediaMTX to explicitly include these IPs/hostnames as valid ICE candidates. This allows WebRTC clients to:
1. Receive `192.168.4.1` as a direct host candidate
2. Connect directly to the local IP without needing STUN
3. Establish the WebRTC connection even without internet access

### How to Revert

Comment out the `webrtcAdditionalHosts` section:
```yaml
# webrtcAdditionalHosts:
#   - localhost
#   - planktoscope.local
#   ...
```

### Deployment

```bash
# On device - edit the config
sudo nano /usr/local/etc/mediamtx.yml
# Add/uncomment webrtcAdditionalHosts as shown above

# Restart MediaMTX
sudo systemctl restart mediamtx

# Verify
sudo systemctl status mediamtx
```

### Expected Outcome

- Video stream works when connected via WiFi hotspot (192.168.4.1)
- Video stream continues to work via ethernet (10.0.0.160)
- No dependency on external STUN servers for local connections

### References

- [MediaMTX WebRTC Connectivity Guide](https://mediamtx.org/docs/usage/webrtc-specific-features#solving-webrtc-connectivity-issues)
- [MediaMTX webrtcAdditionalHosts documentation](https://github.com/bluenviron/mediamtx/blob/main/mediamtx.yml)

**Status:** Applied (2026-01-25)
**Deployment:** Edit `/usr/local/etc/mediamtx.yml` on device, then `sudo systemctl restart mediamtx`

---

## Fix #4: White Balance and LED Intensity Not Persisting

**Date:** 2026-01-25
**Files:**
- `node-red/projects/dashboard/flows.json`
- `default-configs/v3.0.hardware.json`

**Issue:** White balance (red/blue gains) and LED intensity calibration settings don't persist across restarts

### Problem Description

When users calibrate white balance through the UI, the settings are applied but lost after a system restart. Similarly, LED intensity settings don't persist.

**Root Cause:**

1. **Missing save mechanism:** The Node-RED function nodes stored values in global context but never wrote them to `hardware.json`
2. **Missing restore mechanism:** On startup, there was no flow to load calibration values from `hardware.json` into Node-RED global context
3. **Disconnect:** The camera controller reads from `hardware.json`, but Node-RED only saved to its own context storage

### Changes Made

#### Part A: White Balance Save (Function node `d8f732f8fe251222`)

**Original Code:**
```javascript
if (msg.topic) {
    global.set("calibration_wbg_red", msg.payload.settings.white_balance_gain.red);
    global.set("calibration_wbg_blue", msg.payload.settings.white_balance_gain.blue);
}
return msg;
```

**New Code:**
```javascript
if (msg.topic && msg.payload.settings && msg.payload.settings.white_balance_gain) {
    var red = msg.payload.settings.white_balance_gain.red;
    var blue = msg.payload.settings.white_balance_gain.blue;

    // Save to Node-RED context
    global.set("calibration_wbg_red", red);
    global.set("calibration_wbg_blue", blue);

    // Update hardware_conf and save to hardware.json
    // Values divided by 100 (UI sends 199, hardware.json needs 1.99)
    var hardware_conf = global.get("hardware_conf") || {};
    hardware_conf.red_gain = red / 100;
    hardware_conf.blue_gain = blue / 100;
    global.set("hardware_conf", hardware_conf);

    // Return message to trigger file write
    return { payload: hardware_conf, _saveToFile: true };
}
return null;
```

Added nodes: `wb_json_stringify` (JSON) → `wb_save_hardware_config` (file write)

#### Part B: LED Intensity Save (Function node `0283e992ff5da0f6`)

**Original Code:**
```javascript
if (msg.topic) {
    global.set("led_intensity", msg.payload.value);
}
return msg;
```

**New Code:**
```javascript
if (msg.topic && msg.payload.value !== undefined) {
    var intensity = msg.payload.value;

    // Save to Node-RED context
    global.set("led_intensity", intensity);

    // Update hardware_conf and save to hardware.json
    var hardware_conf = global.get("hardware_conf") || {};
    hardware_conf.led_intensity = intensity;
    global.set("hardware_conf", hardware_conf);

    // Return message to trigger file write
    return { payload: hardware_conf, _saveToFile: true };
}
return null;
```

Added nodes: `led_json_stringify` (JSON) → `led_save_hardware_config` (file write)

#### Part C: Startup Restore Flow (New nodes in Setup tab)

Added a startup flow that runs on Node-RED startup:
1. `startup_load_calibration_inject` - Inject node (runs once, 1s delay)
2. `startup_load_hardware_file` - File in node (reads `/home/pi/PlanktoScope/hardware.json`)
3. `startup_parse_hardware_json` - JSON node (parses file contents)
4. `startup_restore_calibration` - Function node (restores values to global context)

```javascript
// Restore function logic:
// Store the full hardware_conf in global context
global.set("hardware_conf", msg.payload);

// Convert from hardware.json format (1.99) to UI format (199)
if (msg.payload.red_gain !== undefined) {
    global.set("calibration_wbg_red", Math.round(msg.payload.red_gain * 100));
}
if (msg.payload.blue_gain !== undefined) {
    global.set("calibration_wbg_blue", Math.round(msg.payload.blue_gain * 100));
}
if (msg.payload.led_intensity !== undefined) {
    global.set("led_intensity", msg.payload.led_intensity);
}
```

#### Part D: Default Config Update

Added `led_intensity` to `default-configs/v3.0.hardware.json`:
```json
{
  ...
  "led_intensity": 1.0,
  ...
}
```

### Data Flow

**On calibration change:**
```
UI → MQTT → Function node → Updates global context
                         → Updates hardware_conf object
                         → JSON stringify → Write to hardware.json
```

**On startup:**
```
Inject (once) → Read hardware.json → Parse JSON → Restore to global context
                                                → calibration_wbg_red
                                                → calibration_wbg_blue
                                                → led_intensity
                                                → hardware_conf
```

**Camera controller startup:**
```
Python controller → Reads hardware.json → Gets red_gain, blue_gain → Applies to camera
```

### Value Conversion

| Location | Red Gain Example | Blue Gain Example |
|----------|------------------|-------------------|
| UI/MQTT | 199 | 165 |
| hardware.json | 1.99 | 1.65 |
| Camera controller | 1.99 | 1.65 |

Conversion: `hardware.json value = UI value / 100`

### How to Revert

1. Restore original function node code (remove hardware_conf updates and file write logic)
2. Remove the added JSON and file nodes (wb_json_stringify, wb_save_hardware_config, led_json_stringify, led_save_hardware_config)
3. Remove the startup flow nodes (startup_load_calibration_inject, startup_load_hardware_file, startup_parse_hardware_json, startup_restore_calibration)
4. Remove `led_intensity` from default-configs/v3.0.hardware.json

### Deployment

```bash
# Deploy Node-RED flows (from local machine)
scp node-red/projects/dashboard/flows.json pi@10.0.0.160:/home/pi/PlanktoScope/node-red/projects/dashboard/

# Restart Node-RED (on device)
sudo systemctl restart nodered

# Verify startup restore worked (check logs)
sudo journalctl -u nodered -n 20 --no-pager | grep "Restore calibration"

# Test:
# 1. Calibrate white balance through UI
# 2. Check hardware.json was updated: cat /home/pi/PlanktoScope/hardware.json
# 3. Restart Node-RED: sudo systemctl restart nodered
# 4. Verify settings persisted in hardware.json and UI
```

### Expected Outcome

- White balance settings (red/blue gains) persist across restarts
- LED intensity settings persist across restarts
- Settings are stored in `/home/pi/PlanktoScope/hardware.json`
- Camera controller reads correct values on startup
- UI displays correct values after restart

**Status:** Applied and deployed to PlanktoScope (2026-01-26)
**Verified:** Startup restore flow logged successful restoration of calibration values

---

## Fix #5: Motion Blur Due to Pump Synchronization Race Condition

**Date:** 2026-01-26
**File:** `controller/imager/main.py`
**Lines:** ~438-445
**Issue:** Intermittent motion blur in captured images (1 in every 2-3 frames blurry)

### Problem Description

During stop-flow acquisition, approximately 1 in every 2-3 captured images showed motion blur, even with a 1-second stabilization delay configured. The blur appeared as horizontal smearing of objects, indicating the sample was still moving during capture.

**Root Cause:** Race condition in MQTT pump synchronization.

When starting a new pump cycle, the sequence was:
1. Acquire lock
2. Clear `_done` event
3. Subscribe to `status/pump` MQTT topic
4. Publish pump command
5. Wait for `_done` event

The bug: Step 3 (subscribe) would receive **stale "Done" messages** from the previous pump cycle still in the MQTT queue. This triggered `_done.set()` before the new pump actually finished, causing the wait to return immediately.

**Evidence from logs:**
```
23:24:07.366 - Subscribe to status/pump (new cycle)
23:24:07.366 - Pump Done (STALE message from previous cycle!)
23:24:07.371 - "The pump has stopped" (processing stale message)
23:24:07.372 - Pump Started (but done event already set!)
23:24:08.371 - Capture (while pump still running - should be ~08.87!)
```

### Original Code (for revert)

In `_receive_messages()` method:
```python
            if self._mqtt.msg["payload"]["status"] not in {"Done", "Interrupted"}:
                loguru.logger.debug(f"Ignoring pump status update: {self._mqtt.msg['payload']}")
                self._mqtt.read_message()
                continue

            loguru.logger.debug(f"The pump has stopped: {self._mqtt.msg['payload']}")
```

### New Code

```python
            if self._mqtt.msg["payload"]["status"] not in {"Done", "Interrupted"}:
                loguru.logger.debug(f"Ignoring pump status update: {self._mqtt.msg['payload']}")
                self._mqtt.read_message()
                continue

            # FIX: Only process Done if we are actually waiting for it
            # This prevents stale Done messages from triggering early return
            if self._done.is_set():
                loguru.logger.debug(f"Ignoring stale pump Done (not waiting): {self._mqtt.msg['payload']}")
                self._mqtt.read_message()
                continue

            loguru.logger.debug(f"The pump has stopped: {self._mqtt.msg['payload']}")
```

### How the Fix Works

1. When a "Done" message arrives, check if `_done.is_set()`
2. If `_done` is already set, we're not waiting for a Done - it's a stale message from a previous pump cycle
3. Stale messages are logged and ignored instead of triggering the done event
4. Only fresh "Done" messages (when `_done` is cleared) are processed

This ensures that only the "Done" message corresponding to the current pump cycle triggers the wait to complete.

### How to Revert

Remove the `time.sleep(0.15)` and second `self._done.clear()` lines from the `run_discrete()` method in `_PumpClient` class.

### Expected Outcome

- All captured images are sharp (taken after proper stabilization)
- Consistent timing between captures (~2.5s for 1.5s pump + 1.0s stabilization)
- No more intermittent motion blur

**Status:** Applied and deployed to PlanktoScope (2026-01-26)

---

## Fix #6: Static Object Detection Not Filtering Debris

**Date:** 2026-01-26
**File:** `segmenter/planktoscope/segmenter/live.py`
**Lines:** 101, 292, 621
**Issue:** Debris stuck on flow cell glass not being filtered during live segmentation

### Problem Description

Objects stuck on the glass (debris) were appearing repeatedly in segmentation results instead of being filtered out. The static object removal feature existed but had two problems:

1. **Disabled by default:** `remove_static` defaulted to `False`
2. **Detection too strict:** 60px grid with 3-frame threshold missed slowly drifting debris due to detection jitter

### Original Code (for revert)

**Line 101:**
```python
self.__static_threshold = 3  # Number of consecutive frames to consider static
```

**Line 292:**
```python
grid_size = 60  # Larger grid tolerates detection variation in big objects
```

**Line 621:**
```python
self.__remove_static = last_message.get("remove_static", False)
```

### New Code

**Line 101:**
```python
self.__static_threshold = 2  # FIX: Reduced from 3 to 2 for faster debris detection
```

**Line 292:**
```python
grid_size = 100  # FIX: Larger grid (was 60) tolerates detection jitter for stuck objects
```

**Line 621:**
```python
self.__remove_static = last_message.get("remove_static", True)
```

### Rationale for Changes

| Parameter | Before | After | Reason |
|-----------|--------|-------|--------|
| `remove_static` default | `False` | `True` | Feature should be on by default since debris is common |
| `grid_size` | 60px | 100px | Larger grid tolerates detection variation where object center jitters between frames |
| `static_threshold` | 3 frames | 2 frames | Faster detection - debris stuck for 2 frames is clearly not a moving organism |

### How Static Detection Works

1. Image divided into grid cells (now 100×100 pixels)
2. Each object's centroid maps to a grid cell: `(int(cx/100), int(cy/100))`
3. Dictionary tracks consecutive frame counts per cell
4. Objects in cells with count ≥ 2 are filtered as "static debris"
5. Counters reset when cell becomes empty

### How to Revert

Restore the original values:
- Line 101: Change `2` back to `3`
- Line 292: Change `100` back to `60`
- Line 621: Change `True` back to `False`

### Expected Outcome

- Debris stuck on glass is filtered after appearing in same position for 2 frames
- Static removal enabled by default for all live segmentation sessions
- Larger grid tolerance handles detection variation without losing accuracy

**Status:** Applied and deployed to PlanktoScope (2026-01-26)

---

## Fix #7: Stabilization Time Too Short

**Date:** 2026-01-26
**File:** `node-red/projects/dashboard/flows.json`
**Node ID:** `bb2825f419cc6526` (function node "start acquisition")
**Issue:** Default 0.5 second stabilization insufficient for sample to fully settle

### Problem Description

The stabilization time (delay between pump stop and image capture) was hardcoded to 0.5 seconds. This was often insufficient for all particles to settle after pump motion, contributing to motion blur.

### Original Code (for revert)

```javascript
msg.payload = {
    action: "image",
    pump_direction: "FORWARD",
    volume: acq_interframe_volume,
    nb_frame: acq_nb_frame,
    sleep: 0.5
};
```

### New Code

```javascript
msg.payload = {
    action: "image",
    pump_direction: "FORWARD",
    volume: acq_interframe_volume,
    nb_frame: acq_nb_frame,
    sleep: 1.0
};
```

### Rationale

- 0.5 seconds: Particles still settling, turbulence from pump motion
- 1.0 seconds: Sufficient time for most particles to fully settle
- Trade-off: Slightly longer acquisition time (adds 0.5s per frame)

### How to Revert

In Node-RED flows.json, find node `bb2825f419cc6526` and change `sleep: 1.0` back to `sleep: 0.5`.

### Expected Outcome

- All particles fully settled before capture
- Reduced motion blur from residual fluid motion
- Acquisition time increases by ~0.5 seconds per frame

**Status:** Applied and deployed to PlanktoScope (2026-01-26)

---

## Fix #6: Live Segmentation Pixel Size Inconsistency

**Date:** 2026-01-26
**File:** `segmenter/planktoscope/segmenter/live.py`
**Lines:** 54, 101, 114-141

**Issue:** Live segmenter used hardcoded pixel size (0.75 µm/pixel) instead of reading from calibration config

### Problem Description

The live segmentation module had the pixel size hardcoded to 0.75 µm/pixel. This caused inconsistencies when users calibrated their PlanktoScope to a different pixel size via the calibration dashboard (`/calibration_pixel_size`). The min ESD filter would use the wrong conversion factor, potentially filtering out objects incorrectly.

**Root Cause:** The `__pixel_size_um` value was set to a constant `0.75` instead of reading from `/home/pi/PlanktoScope/hardware.json` like the rest of the system.

### Original Code (for revert)

```python
# Line 98
self.__pixel_size_um = 0.75  # Micrometers per pixel (typical PlanktoScope value)
```

### New Code

```python
# Line 54 - Added constant
HARDWARE_CONFIG_PATH = "/home/pi/PlanktoScope/hardware.json"

# Line 101 - Changed initialization
self.__pixel_size_um = self._load_pixel_size()  # Load from hardware config

# Lines 114-141 - Added method
def _load_pixel_size(self):
    """Load pixel size from hardware config file.

    Reads process_pixel_fixed from /home/pi/PlanktoScope/hardware.json.
    This ensures consistency with the calibration value set in the dashboard.

    Returns:
        float: Pixel size in micrometers per pixel. Defaults to 0.75 if not found.
    """
    default_pixel_size = 0.75
    try:
        with open(HARDWARE_CONFIG_PATH, "r") as f:
            config = json.load(f)
            pixel_size = config.get("process_pixel_fixed", default_pixel_size)
            logger.info(f"Loaded pixel size from hardware config: {pixel_size} µm/pixel")
            return float(pixel_size)
    except FileNotFoundError:
        logger.warning(
            f"Hardware config not found at {HARDWARE_CONFIG_PATH}, "
            f"using default pixel size: {default_pixel_size} µm/pixel"
        )
        return default_pixel_size
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(
            f"Error reading hardware config: {e}, "
            f"using default pixel size: {default_pixel_size} µm/pixel"
        )
        return default_pixel_size
```

### How to Revert

Replace line 101 with:
```python
self.__pixel_size_um = 0.75  # Micrometers per pixel (typical PlanktoScope value)
```

And remove the `_load_pixel_size` method and `HARDWARE_CONFIG_PATH` constant.

### Expected Outcome

- Live segmentation uses the same pixel size as set in the calibration dashboard
- Min ESD filter correctly converts micrometers to pixels
- Consistent object detection between live preview and post-acquisition segmentation

**Status:** Applied (2026-01-26)

---
