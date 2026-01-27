# PlanktoScope Update Dashboard - Release Documentation


**Date:** 2026-01-26 (Updated)
**Base Repository/Branch:** PlanktoScope Dashboard 2.0 - update-dashboard
**Author:** Adam Larson

---


This release implements two major feature enhancements requested via GitHub issues, along with critical bug fixes identified during deployment testing on Raspberry Pi 5 hardware. The changes enable real-time plankton detection during sample acquisition and provide quantitative focus quality metrics for quality assurance.

### Changes Overview

| Category | Description | Priority | Status |
|----------|-------------|----------|--------|
| **PR #1** | Live Segmentation Feature | High | Complete |
| **PR #2** | Blur/Focus Quality Metric | High | Complete |
| **Bug Fix #1** | H.264 Video Stream Corruption (RPi5) | High | Complete |
| **Bug Fix #2** | Calibration Settings Persistence (flushInterval) | High | Complete |
| **Bug Fix #3** | Video Stream Not Working Over WiFi Hotspot | High | Complete |
| **Bug Fix #4** | White Balance & LED Intensity Not Persisting | High | Complete |
| **Bug Fix #5** | Motion Blur from Pump Sync Race Condition | High | Complete |
| **Bug Fix #6** | Static Object Detection Improvements | Medium | Complete |
| **Bug Fix #7** | Stabilization Time Increased | Medium | Complete |

---

## PR #1: Live Segmentation Feature

### Problem 

Operators had no real-time feedback during sample acquisition. They could only assess sample quality and object detection after the acquisition completed, leading to wasted time on poorly focused or improperly positioned samples.

### Solution Implemented

A real-time segmentation system that processes each captured frame during acquisition, overlays detected objects on a live preview, and provides immediate visual feedback to operators.

### Architecture

```
┌─────────────────────────┐     MQTT: segmenter/live        ┌────────────────────────┐
│   Frontend (SolidJS)    │ ──────────────────────────────> │   LiveSegmenterProcess │
│   - Visualization Page  │                                 │   (Python/OpenCV)      │
│   - Canvas Overlay      │ <────────────────────────────── │                        │
│   - Controls UI         │   MQTT: status/segmenter/live   │   Subscribes to:       │
└─────────────────────────┘                                 │   status/imager        │
                                                            └────────────────────────┘
```

### Files Added

#### 1. `segmenter/planktoscope/segmenter/live.py` (NEW - 450 lines)

**Purpose:** Backend process for real-time frame segmentation.

**Key Implementation Details:**

```python
class LiveSegmenterProcess(multiprocessing.Process):
    """
    Runs as a separate process to avoid blocking the main segmenter.
    Subscribes to imager capture events and processes each frame.
    """
```

**Core Methods:**

| Method | Purpose |
|--------|---------|
| `segment_single_frame(img)` | Main entry point - segments one frame, returns objects + blur |
| `_create_simple_mask(img)` | Binary mask using adaptive threshold + morphological ops |
| `_load_pixel_size()` | Loads `process_pixel_fixed` from `/home/pi/PlanktoScope/hardware.json` |
| `_esd_um_to_min_area(esd_um)` | Converts µm filter to pixel area using loaded calibration |
| `_encode_mask_png(mask)` | Base64 PNG encoding with alpha transparency |
| `_is_static_object(bbox)` | Grid-based debris detection (100px cells, 2-frame threshold) |

**Pixel Size Calibration:**

The live segmenter reads pixel size from `/home/pi/PlanktoScope/hardware.json` (`process_pixel_fixed` field) to ensure consistency with the calibration dashboard. Falls back to 0.75 µm/pixel if config unavailable.

**Improved Static Object Detection Algorithm:**

The system tracks object positions across frames to identify debris stuck on the flow cell glass:

1. Image divided into 100×100 pixel grid cells
2. Each object's centroid maps to a grid cell
3. Dictionary tracks consecutive frame counts per cell
4. Objects in cells with count ≥2 are filtered as "static"
5. Counters reset when cell becomes empty

**Rationale for Parameters:**
- **100px grid size:** Tolerates detection jitter while distinguishing separate objects
- **2-frame threshold:** Faster debris detection (objects stuck on glass are truly stationary)

**Performance Limits:**
- Maximum 300 objects per frame (prevents UI lag)
- Maximum 100 masks encoded (masks are memory-intensive)
- JPEG quality 80% for reasonable bandwidth

---

#### 2. `segmenter/main.py` (MODIFIED)

**Change:** Added live segmenter process initialization.

```python
# ADDED: Import and start live segmenter
import planktoscope.segmenter.live

live_segmenter_thread = planktoscope.segmenter.live.LiveSegmenterProcess(
    shutdown_event, "/home/pi/data"
)
live_segmenter_thread.start()
```

**Rationale:** Separate process ensures live preview doesn't impact main segmentation performance during post-acquisition batch processing.

---

#### 3. `frontend/src/pages/preview/segmentation/index.jsx` (NEW - 482 lines)

**Purpose:** Live Segmentation Visualization page embedded in Node-RED dashboard.

**State Management:**
```javascript
const [liveSegmentEnabled, setLiveSegmentEnabled] = createSignal(false)
const [overlayMode, setOverlayMode] = createSignal("bbox")  // bbox | mask | both
const [minSizeUm, setMinSizeUm] = createSignal(20)          // µm minimum ESD
const [removeStatic, setRemoveStatic] = createSignal(true)  // debris filter
const [objects, setObjects] = createSignal([])              // detected objects
```

**Overlay Rendering:**
```javascript
function drawOverlays() {
    // Scale from original image coordinates to display coordinates
    const scaleX = displayWidth / imageRef.naturalWidth
    const scaleY = displayHeight / imageRef.naturalHeight

    objects().forEach((obj) => {
        const [x, y, w, h] = obj.bbox
        // Draw cyan bounding box and/or semi-transparent mask
    })
}
```

**Design Decision - Cyan Color Scheme:**
- Bounding box: `rgb(0, 128, 128)` (teal)
- Mask fill: `rgb(0, 220, 220)` (cyan) at 35% opacity
- Rationale: High contrast against biological samples, professional microscopy aesthetic Thibaut likes 

---

#### 4. `frontend/src/pages/preview/segmentation/styles.module.css` (NEW - 352 lines)

CSS module providing dark theme styling consistent with Node-RED dashboard.

---

#### 5. `lib/scope.js` (MODIFIED)

**Added Functions:**
```javascript
export async function startLiveSegmentation(config) {
    // config: { overlay: "bbox", min_esd_um: 20, remove_static: true }
    await request("segmenter/live", { action: "start", ...config })
}

export async function stopLiveSegmentation() {
    await request("segmenter/live", { action: "stop" })
}
```

---

### MQTT Interface

| Topic | Direction | Payload |
|-------|-----------|---------|
| `segmenter/live` | Frontend → Backend | `{"action": "start", "overlay": "bbox", "min_esd_um": 20, "remove_static": true}` |
| `segmenter/live` | Frontend → Backend | `{"action": "stop"}` |
| `status/segmenter/live` | Backend → Frontend | `{"status": "Enabled", "overlay": "bbox"}` |
| `status/segmenter/live` | Backend → Frontend | `{"objects": [...], "frame_blur": 45.2, "image": "base64...", "image_width": 4056, "image_height": 3040}` |

---

## PR #2: Blur/Focus Quality Metric

### Problem Statement

Operators needed quantitative feedback on image focus quality to:
1. Assess sample positioning in real-time
2. Identify focus drift during long acquisitions
3. Filter poor-quality images in post-processing

### Solution Implemented

A Laplacian variance-based blur metric with real-time visualization including sparkline trending and optional spatial heatmap overlay.

### Technical Background

**Laplacian Variance Method:**

The Laplacian operator detects edges by computing the second derivative of image intensity. Sharp images have strong edges (high variance), while blurry images have weak edges (low variance).

```python
def calculate_blur(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return cv2.Laplacian(gray, cv2.CV_64F).var()
```

**Calibration for PlanktoScope Optics:**

Empirical testing with the PlanktoScope optical system established these thresholds:

| Blur Value | Quality | Visual Indicator |
|------------|---------|------------------|
| < 25 | Poor | Red |
| 25 - 50 | Acceptable | Yellow |
| > 50 | Good | Green |

**Rationale:** These thresholds were calibrated against manual focus assessment by trained operators using the specific optical configuration (IMX477 sensor, 25mm/12mm lens configuration).

### Files Modified

#### 1. `segmenter/planktoscope/segmenter/operations.py` (MODIFIED)

**Added Functions:**

```python
def calculate_blur(img):
    """Calculate blur metric using Laplacian variance.

    Args:
        img: BGR or grayscale image
    Returns:
        float: Higher = sharper, Lower = blurrier
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def calculate_regional_blur(img, grid_rows=4, grid_cols=4):
    """Calculate blur for each region of the image.

    Returns 4x4 grid of blur values for spatial focus assessment.
    Useful for identifying tilt or uneven focus plane.
    """
    # Divides image into grid, computes Laplacian variance per cell
    # Returns: list[list[float]] shape [grid_rows][grid_cols]
```

**Regional Blur Rationale:**

A 4×4 grid provides sufficient spatial resolution to detect:
- Sample tilt (gradient across image)
- Partial occlusion
- Debris on optical path
- Non-uniform illumination effects

---

#### 2. `segmenter/planktoscope/segmenter/live.py` (MODIFIED)

**Integration:**

```python
# In segment_single_frame():
frame_blur = planktoscope.segmenter.operations.calculate_blur(img)
blur_grid = planktoscope.segmenter.operations.calculate_regional_blur(img, 4, 4)

return {
    "objects": objects,
    "frame_blur": float(frame_blur),
    "blur_grid": blur_grid,  # 4x4 regional heatmap data
    # ...
}
```

---

#### 3. `frontend/src/pages/preview/segmentation/index.jsx` (MODIFIED)

**Added State:**
```javascript
const [blurHistory, setBlurHistory] = createSignal([])  // Last 60 values
const [blurGrid, setBlurGrid] = createSignal(null)       // 4x4 regional data
const [showHeatmap, setShowHeatmap] = createSignal(false)
```

**Sparkline Implementation:**
```javascript
const sparklinePath = () => {
    const history = blurHistory()
    if (history.length < 2) return ""

    // SVG path generation for 140x40 sparkline
    const points = history.map((value, index) => {
        const x = padding + (index / (BLUR_HISTORY_SIZE - 1)) * (width - 2 * padding)
        const y = height - padding - ((value - min) / range) * (height - 2 * padding)
        return `${x},${y}`
    })
    return `M ${points.join(" L ")}`
}
```

**Heatmap Rendering:**
```javascript
function drawHeatmap() {
    // Color mapping: red (blurry) → yellow → green (sharp)
    const hue = normalized * 120  // 0=red, 60=yellow, 120=green
    ctx.fillStyle = `hsla(${hue}, 80%, 50%, 0.35)`
}
```

**UI Layout:**

The blur visualization appears as a floating overlay panel in the bottom-right corner of the segmentation preview, containing:
- Current blur value (large, color-coded)
- Sparkline (last 60 frames)
- Min/Avg/Max statistics
- Heatmap toggle button

---

### EcoTaxa Integration

Per-object blur is exported to the TSV file for post-acquisition quality filtering:

```
object_blur_laplacian	45.23
```

This enables researchers to filter the dataset by focus quality during analysis.

---

## Bug Fix: H.264 Video Stream Corruption (RPi5)

### Problem Statement

Severe video corruption manifested as blocky pixelization artifacts on Raspberry Pi 5 hardware. The live preview stream was unustable, displaying what appeared to be DivX-era compression artifacts.

### Root Cause Analysis

**Finding 1: Resolution Misalignment**

The original RPi5 preview resolution `2028×1520` violates H.264 macroblock alignment requirements:
- H.264 requires dimensions divisible by 16 (macroblock size)
- 2028 ÷ 16 = 126.75 ❌
- 1520 ÷ 16 = 95 ✓

The RPi4 resolution `1440×1080` was properly aligned

**Finding 2: B-Frame Incompatibility**

Research identified that WebRTC (used by MediaMTX for browser streaming) does not support H.264 B-frames:
- Default H.264 profile uses B-frames for compression efficiency
- WebRTC decoders cannot process B-frames correctly
- Results in frame reordering artifacts

**References:**
- https://github.com/bluenviron/mediamtx/issues/3022
- https://github.com/raspberrypi/picamera2/issues/785

### Changes Applied

#### 1. `controller/camera/hardware.py`

**Resolution Fix (Line 21):**

| Before | After |
|--------|-------|
| `(2028, 1520)` | `(1920, 1440)` |

**Rationale for 1920×1440:**
- 1920 ÷ 16 = 120 ✓
- 1440 ÷ 16 = 90 ✓
- Maintains 4:3 aspect ratio
- Standard resolution with broad decoder support

**Encoder Configuration (Lines 287-301):**

```python
# BEFORE
encoder = encoders.H264Encoder()

# AFTER
encoder = encoders.H264Encoder(
    profile="baseline",  # Disables B-frames
    repeat=True,         # Repeat SPS/PPS headers
    iperiod=15,          # I-frame every 15 frames
)
```

**Parameter Rationale:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `profile="baseline"` | Baseline H.264 | Disables B-frames for WebRTC compatibility |
| `repeat=True` | Enable | Repeat sequence headers with each I-frame for network resilience |
| `iperiod=15` | 15 frames | Balance between compression and error recovery |

---

#### 2. `os/mediamtx/mediamtx.yml`

**Added:**
```yaml
writeQueueSize: 1024
```

**Rationale:** The RPi5 software encoder can produce data faster than the default buffer allows, causing packet drops. Increased buffer prevents overflow.

---

### Outcome

**Status: Partial Success**

The changes significantly reduced but did not completely eliminate stream artifacts. Remaining issues are likely related to:
- RPi5 software encoder limitations (no hardware H.264)
- Network latency variations
- Browser decoder variations

**Recommendation:** Consider hardware-accelerated encoding solutions or alternative streaming protocols (MJPEG) for production deployment.

---

## Bug Fix: Calibration Settings Persistence

### Problem Statement

Calibration settings (pixel size, white balance gains, pump steps/mL) were lost on system restart, requiring operators to recalibrate after each power cycle.

### Root Cause

Node-RED's `localfilesystem` context storage module flushes to disk every 30 seconds by default. If the system restarts within this window, unsaved calibration data is lost.

### Solution

#### `node-red/settings.cjs` (Lines 341-345)

```javascript
// BEFORE
contextStorage: {
   default: {
       module: "localfilesystem"
   },
},

// AFTER
contextStorage: {
   default: {
       module: "localfilesystem",
       config: {
           flushInterval: 5,  // Flush every 5 seconds
       }
   },
},
```

### Calibration Data Protected

| Variable | Description |
|----------|-------------|
| `calibration_pixel_size` | µm/pixel from ruler calibration |
| `calibration_scale_factor` | Sensor to stream scale ratio |
| `calibration_wbg_red` | White balance red gain |
| `calibration_wbg_blue` | White balance blue gain |
| `calibration_nb_step` | Pump steps per mL |
| `calibration_markerA_*` | Calibration marker positions |
| `calibration_markerB_*` | Calibration marker positions |

### Trade-offs

| Consideration | Impact |
|---------------|--------|
| Increased disk I/O | Negligible (writes small JSON every 5s) |
| SD card wear | Minimal (< 1KB per write) |
| Data loss window | Reduced from 30s to 5s |

---

## Bug Fix #3: Video Stream Not Working Over WiFi Hotspot

### Problem Statement

Video streams work over ethernet but fail when connecting via the PlanktoScope's WiFi hotspot. The UI loads correctly but the video stream shows a spinning wheel indefinitely.

### Root Cause

WebRTC ICE candidate gathering fails on the hotspot network because:
1. MediaMTX relied on public STUN servers (Cloudflare, Mozilla, Meta) for ICE candidate discovery
2. The hotspot network (192.168.4.0/24) typically has no internet access
3. STUN servers are unreachable → ICE gathering times out → WebRTC connection fails

### Solution

Enabled `webrtcAdditionalHosts` in MediaMTX configuration to explicitly advertise local IPs as valid ICE candidates, bypassing the need for STUN:

```yaml
webrtcAdditionalHosts:
  - localhost
  - planktoscope.local
  - pkscope.local
  - 192.168.4.1
  - 10.0.0.160
  - planktoscope-butter-earth
  - planktoscope-butter-earth.local
  - home.pkscope
```

### Files Modified

| File | Change |
|------|--------|
| `os/mediamtx/mediamtx.yml` | Added `webrtcAdditionalHosts` configuration |
| `/usr/local/etc/mediamtx.yml` (on device) | Same configuration applied |

---

## Bug Fix #4: White Balance and LED Intensity Not Persisting

### Problem Statement

White balance (red/blue gains) and LED intensity calibration settings were lost after system restart, even though the flushInterval fix (Bug Fix #2) was applied.

### Root Cause

The flushInterval fix only addressed Node-RED context storage. However:
1. **No save mechanism:** Function nodes stored values in Node-RED context but never wrote to `hardware.json`
2. **No restore mechanism:** On startup, no flow loaded values from `hardware.json` into Node-RED context
3. **Disconnect:** Camera controller reads from `hardware.json`, but Node-RED only saved to its own context

### Solution

Implemented a complete persistence pipeline:

1. **Save on change:** Modified function nodes to write calibration values to `hardware.json` when changed
2. **Restore on startup:** Added startup flow to load values from `hardware.json` into Node-RED context
3. **Value conversion:** Handle the conversion between UI format (199) and hardware.json format (1.99)

### Files Modified

| File | Change |
|------|--------|
| `node-red/projects/dashboard/flows.json` | Modified WB/LED function nodes, added save nodes, added startup restore flow |
| `default-configs/v3.0.hardware.json` | Added `led_intensity` field |

### Data Flow

```
On Change:  UI → MQTT → Function → Update global context → Write hardware.json
On Startup: Inject → Read hardware.json → Parse → Restore global context
```

---

## Deployment Summary

### Files Added (New)

| File | Lines | Purpose |
|------|-------|---------|
| `segmenter/planktoscope/segmenter/live.py` | ~450 | Live segmentation backend |
| `frontend/src/pages/preview/segmentation/index.jsx` | ~482 | Visualization page |
| `frontend/src/pages/preview/segmentation/styles.module.css` | ~352 | Styling |
| `frontend/src/pages/preview/SegmentationOverlay.jsx` | ~368 | Overlay component |
| `frontend/src/pages/preview/SegmentationOverlay.module.css` | ~102 | Overlay styling |

### Files Modified

| File | Changes |
|------|---------|
| `segmenter/main.py` | Added live segmenter process start |
| `segmenter/planktoscope/segmenter/operations.py` | Added `calculate_blur()`, `calculate_regional_blur()` |
| `segmenter/planktoscope/segmenter/__init__.py` | Added `segment_single_frame()` helper |
| `lib/scope.js` | Added `startLiveSegmentation()`, `stopLiveSegmentation()` |
| `controller/camera/hardware.py` | Resolution fix, encoder parameters |
| `os/mediamtx/mediamtx.yml` | Added `writeQueueSize: 1024`, added `webrtcAdditionalHosts` |
| `node-red/settings.cjs` | Added `flushInterval: 5` |
| `node-red/projects/dashboard/flows.json` | Added WB/LED persistence, startup restore flow |
| `default-configs/v3.0.hardware.json` | Added `led_intensity` field |

### Deployment Commands

```bash
# Frontend deployment
cd frontend && npx vite build
scp -r dist/* pi@planktoscope.local:/home/pi/PlanktoScope/frontend/dist/

# Backend deployment
scp segmenter/planktoscope/segmenter/live.py pi@planktoscope.local:/home/pi/PlanktoScope/segmenter/planktoscope/segmenter/
scp segmenter/planktoscope/segmenter/operations.py pi@planktoscope.local:/home/pi/PlanktoScope/segmenter/planktoscope/segmenter/

# Node-RED settings
scp node-red/settings.cjs pi@planktoscope.local:/home/pi/PlanktoScope/node-red/
sudo systemctl restart nodered

# Restart segmenter
sudo systemctl restart segmenter
```

---

## Testing Checklist

### Live Segmentation
- [ ] Enable live segmentation on Visualization page
- [ ] Start acquisition and verify objects appear with overlays
- [ ] Test overlay modes: bbox, mask, both
- [ ] Adjust minimum size filter, verify small objects filtered
- [ ] Enable "Remove Static", verify debris filtered after 3 frames
- [ ] Verify object count updates in real-time

### Blur Metric
- [ ] Verify focus value displayed during acquisition
- [ ] Confirm color coding: red (<25), yellow (25-50), green (>50)
- [ ] Verify sparkline shows trending history
- [ ] Toggle heatmap overlay, verify regional display
- [ ] Check EcoTaxa TSV contains `object_blur_laplacian` column

### Video Stream (RPi5)
- [ ] Verify preview stream displays without severe corruption
- [ ] Test stream recovery after network interruption

### Video Stream Over WiFi Hotspot
- [ ] Connect to PlanktoScope WiFi hotspot
- [ ] Access UI at http://192.168.4.1
- [ ] Verify video stream loads and displays
- [ ] Test stream while disconnected from ethernet (hotspot only)

### Calibration Persistence (Node-RED Context)
- [ ] Perform calibration (pixel size or white balance)
- [ ] Restart Node-RED service
- [ ] Verify calibration values persisted

### White Balance & LED Intensity Persistence (hardware.json)
- [ ] Calibrate white balance through UI
- [ ] Verify `hardware.json` contains updated `red_gain` and `blue_gain`
- [ ] Adjust LED intensity
- [ ] Verify `hardware.json` contains updated `led_intensity`
- [ ] Restart Node-RED service
- [ ] Verify UI shows correct values after restart
- [ ] Restart entire system (reboot)
- [ ] Verify camera applies correct white balance on startup

---

## Known Limitations

1. **Video Stream (RPi5):** Some residual artifacts may occur due to software encoder limitations
2. **Live Segmentation Performance:** Maximum 300 objects/frame to prevent UI lag
3. **Blur Thresholds:** Calibrated for PlanktoScope optics; may need adjustment for different configurations
4. **WiFi Hotspot mDNS:** When connecting via hotspot, use IP address (192.168.4.1) rather than `.local` hostnames for most reliable connectivity
5. **MediaMTX Restart:** After restarting MediaMTX, the imager service may need to be restarted to re-establish RTSP publishing

---

## Bug Fix #5: Motion Blur from Pump Synchronization Race Condition

### Problem Statement

During stop-flow acquisition, approximately 1 in every 2-3 captured images showed motion blur, even with adequate stabilization delay. Images were captured while the pump was still running.

### Root Cause

Race condition in MQTT pump synchronization: When starting a new pump cycle, stale "Done" messages from the previous cycle would trigger `_done.set()` before the new pump completed, causing capture to happen prematurely.

### Solution

Modified `_receive_messages()` in `controller/imager/main.py` to check if we're actually waiting for a "Done" message before processing it:

```python
# FIX: Only process Done if we are actually waiting for it
if self._done.is_set():
    loguru.logger.debug(f"Ignoring stale pump Done (not waiting)")
    self._mqtt.read_message()
    continue
```

### Outcome

All captures now occur after proper stabilization. No more intermittent motion blur.

---

## Bug Fix #6: Static Object Detection Improvements

### Problem Statement

Debris stuck on flow cell glass was not being filtered during live segmentation despite the static object removal feature existing.

### Root Cause

1. `remove_static` defaulted to `False` (disabled)
2. 60px grid was too small - detection jitter caused objects to shift between grid cells
3. 3-frame threshold was too strict for quickly identifying debris

### Solution

| Parameter | Before | After |
|-----------|--------|-------|
| `remove_static` default | `False` | `True` |
| `grid_size` | 60px | 100px |
| `static_threshold` | 3 frames | 2 frames |

### Outcome

Debris on glass is now filtered after appearing in the same position for 2 consecutive frames.

---

## Bug Fix #7: Stabilization Time Increased

### Problem Statement

Default 0.5 second stabilization was insufficient for particles to fully settle after pump motion.

### Solution

Changed `sleep` parameter in Node-RED flows from `0.5` to `1.0` seconds.

### Outcome

Adequate settling time for most samples. Adds ~0.5s per frame to acquisition time.

---

## Appendix: Blur Metric Scientific Basis

The Laplacian variance method is a well-established focus measure in computer vision literature:

**Method:** Computes the variance of the Laplacian (second derivative) of image intensity.

**Mathematical Basis:**
```
Blur = Var(∇²I)
```

Where `∇²I` is the Laplacian of image `I`.

**Properties:**
- Higher variance indicates more edges (sharper focus)
- Lower variance indicates fewer edges (blur)
- Computationally efficient (single convolution)
- Robust to image content variations

**Reference:** Pech-Pacheco, J.L., et al. "Diatom autofocusing in brightfield microscopy: a comparative study." ICPR 2000.

---


