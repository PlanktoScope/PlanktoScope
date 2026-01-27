# Live Segmentation and Blur Metric Features - Code Changes

This document describes the code changes made to the Dashboard 2.0 repository to implement real-time segmentation with preview during acquisition.  In addition, a blur metric is now calculated per object.

## Overview

The Live Segmentation feature provides real-time object detection and visualization during image acquisition. When enabled, each captured frame is segmented and the results are overlaid on a separate preview window, allowing users to see detected plankton objects in real-time.  A blur metric is also captured per object, allowing live feedback as well as post acquisition sorting through the .tsv file. 

### Key Features
- **Real-time object detection** during acquisition
- **Configurable overlay modes**: Bounding boxes, masks, or both
- **Minimum size filter** (in micrometers) to ignore small objects
- **Static object removal** to filter out debris stuck on the flow cell glass
- **Focus/blur indicator** to assess image quality in real-time

---

## Architecture

```
┌─────────────────────┐     MQTT: segmenter/live      ┌──────────────────────┐
│   Frontend          │ ────────────────────────────> │   Live Segmenter     │
│   (SolidJS)         │                               │   (Python Process)   │
│                     │ <──────────────────────────── │                      │
│   Canvas Overlay    │   MQTT: status/segmenter/live │   Listens to imager  │
└─────────────────────┘                               └──────────────────────┘
                                                              │
                                                              │ MQTT: status/imager
                                                              ▼
                                                      ┌──────────────────────┐
                                                      │   Imager Process     │
                                                      │   (captures images)  │
                                                      └──────────────────────┘
```

---

## File Changes

### Backend (Python)

#### 1. `segmenter/main.py`
**Change**: Added initialization of the Live Segmenter process.

```python
import planktoscope.segmenter.live

# Starts the live segmenter process for real-time preview overlays
live_segmenter_thread = planktoscope.segmenter.live.LiveSegmenterProcess(
    shutdown_event, "/home/pi/data"
)
live_segmenter_thread.start()
```

The live segmenter runs as a separate multiprocessing.Process alongside the main segmenter.

---

#### 2. `segmenter/planktoscope/segmenter/live.py` (NEW FILE)
**Purpose**: Handles real-time segmentation during acquisition.

**Key Components**:

##### Class: `LiveSegmenterProcess`
A multiprocessing.Process that:
1. Listens for control commands on `segmenter/live` MQTT topic
2. Subscribes to `status/imager` to receive capture events
3. Segments each captured frame and publishes results

##### Key Methods:

**`_load_pixel_size()`**
Loads the pixel size calibration from the hardware config file to ensure consistency with the dashboard calibration settings:
```python
def _load_pixel_size(self):
    """Load pixel size from /home/pi/PlanktoScope/hardware.json.
    Returns process_pixel_fixed value, or 0.75 as fallback."""
    try:
        with open("/home/pi/PlanktoScope/hardware.json", "r") as f:
            config = json.load(f)
            return float(config.get("process_pixel_fixed", 0.75))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 0.75  # Default fallback
```

**`_esd_um_to_min_area(esd_um)`**
Converts minimum object size from micrometers (ESD) to pixel area:
```python
def _esd_um_to_min_area(self, esd_um):
    esd_pixels = esd_um / self.__pixel_size_um  # Loaded from hardware.json
    area = math.pi * (esd_pixels / 2) ** 2
    return int(area)
```

**`_create_simple_mask(img)`**
Creates a binary mask using the same pipeline as the main segmenter:
```python
def _create_simple_mask(self, img):
    mask = planktoscope.segmenter.operations.simple_threshold(img)
    mask = planktoscope.segmenter.operations.erode(mask)
    mask = planktoscope.segmenter.operations.dilate(mask)
    return mask
```

**Static Object Detection** (`_get_bbox_key`, `_update_static_tracker`, `_is_static_object`)

Uses grid-based tracking to identify objects that remain in the same position across multiple frames:

```python
def _get_bbox_key(self, bbox):
    """Get grid cell for object center (60px grid)"""
    cx = bbox[0] + bbox[2] / 2
    cy = bbox[1] + bbox[3] / 2
    grid_size = 60
    return (int(cx / grid_size), int(cy / grid_size))

def _is_static_object(self, bbox):
    """Returns True if object has been in same position for 3+ frames"""
    key = self._get_bbox_key(bbox)
    count = self.__static_tracker.get(key, 0)
    return count >= self.__static_threshold  # threshold = 3
```

**Logic**: Objects must appear in the same 60px grid cell for 3 consecutive frames to be considered static (debris stuck on glass) and filtered out.

**`_encode_mask_png(mask)`**
Encodes binary masks as base64 PNG with alpha transparency:
```python
def _encode_mask_png(self, mask):
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    rgba[mask, :3] = 255  # White RGB for object pixels
    rgba[mask, 3] = 255   # Full opacity
    # Background = (0,0,0,0) = transparent
    img = PIL.Image.fromarray(rgba, mode="RGBA")
    # ... encode as base64 PNG
```

**`segment_single_frame(img)`**
Main segmentation entry point. Returns:
```python
{
    "objects": [{"bbox": [x, y, w, h], "mask": "base64..."}],
    "frame_blur": float,
    "object_count": int,
    "image_width": int,
    "image_height": int
}
```

##### MQTT Interface:

| Topic | Direction | Payload |
|-------|-----------|---------|
| `segmenter/live` | Frontend → Backend | `{"action": "start/stop", "overlay": "bbox/mask/both", "min_esd_um": 20, "remove_static": true}` |
| `status/segmenter/live` | Backend → Frontend | `{"objects": [...], "frame_blur": float, "image": "base64_jpeg"}` |

---

#### 3. `segmenter/planktoscope/segmenter/operations.py`
**Change**: Added blur calculation function.

```python
def calculate_blur(img):
    """Calculate blur metric using Laplacian variance.

    Higher values = sharper image, lower values = more blur.

    Args:
        img (cv2 img): Image to calculate blur for (BGR or grayscale)

    Returns:
        float: Laplacian variance (blur metric)
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return cv2.Laplacian(gray, cv2.CV_64F).var()
```

**Calibration for PlanktoScope optics**:
- Poor focus: < 25
- OK focus: 25-50
- Good focus: > 50

---

#### 4. `segmenter/planktoscope/segmenter/__init__.py`
**Change**: Added helper function for live segmentation.

```python
def segment_single_frame(img, min_area=100):
    """Segment a single frame and return object data without file I/O.

    This is a helper function for live segmentation that returns object
    metadata without saving to disk.
    """
    # ... segmentation pipeline identical to main segmenter
```

Also integrated per-object blur calculation into the EcoTaxa export metadata.

---

### Frontend (SolidJS)

#### 5. `frontend/src/pages/preview/segmentation/index.jsx` (NEW FILE)
**Purpose**: Live Segmentation Preview page with controls and overlay.

**State Management**:
```javascript
const [liveSegmentEnabled, setLiveSegmentEnabled] = createSignal(false)
const [overlayMode, setOverlayMode] = createSignal("bbox")
const [minSizeUm, setMinSizeUm] = createSignal(20)
const [removeStatic, setRemoveStatic] = createSignal(true)
const [frameBlur, setFrameBlur] = createSignal(0)
const [objectCount, setObjectCount] = createSignal(0)
const [capturedImage, setCapturedImage] = createSignal(null)
const [objects, setObjects] = createSignal([])
```

**Overlay Drawing**:
```javascript
function drawOverlays() {
    // Scale coordinates from original image to display size
    const scaleX = displayWidth / imageRef.naturalWidth
    const scaleY = displayHeight / imageRef.naturalHeight

    objects().forEach((obj, index) => {
        const [x, y, w, h] = obj.bbox
        const scaledX = x * scaleX
        // ... draw bounding boxes and/or masks
    })
}
```

**Focus Indicator**:
```javascript
const focusStatus = () => {
    const blur = frameBlur()
    if (blur < 25) return { label: "Poor", icon: "✗", color: "#ef4444" }
    if (blur < 50) return { label: "OK", icon: "~", color: "#eab308" }
    return { label: "Good", icon: "✓", color: "#22c55e" }
}
```

---

#### 6. `frontend/src/pages/preview/segmentation/styles.module.css` (NEW FILE)
CSS styles for the segmentation preview page including:
- Dark theme toolbar
- Toggle switch for enabling/disabling
- Mode selector dropdown
- Number input for minimum size
- Stats display (object count, focus status)

---

#### 7. `lib/scope.js`
**Change**: Added live segmentation control functions.

```javascript
export async function startLiveSegmentation(config) {
    await request("segmenter/live", { action: "start", ...config })
}

export async function stopLiveSegmentation() {
    await request("segmenter/live", { action: "stop" })
}
```

---

## Static Object Removal Algorithm

The static removal feature filters out debris stuck on the flow cell glass by tracking object positions across frames.

### How It Works:

1. **Grid-Based Tracking**: The image is divided into 60px grid cells
2. **Position Hashing**: Each object's center point maps to a grid cell
3. **Frame Counting**: A dictionary tracks how many consecutive frames each grid cell has contained an object
4. **Filtering**: Objects in cells with count >= 3 are considered static and filtered out
5. **Automatic Cleanup**: When a position has no object in a frame, its counter is removed

### Why 60px Grid?
- **Too small** (e.g., 30px): Large objects may shift between cells due to slight detection variation
- **Too large** (e.g., 100px): Multiple separate small objects might be grouped together
- **60px**: Good balance for typical PlanktoScope object sizes

### Why 3-Frame Threshold?
- Ensures objects are truly static, not just slow-moving
- Avoids false positives from coincidental position overlap
- Quick enough to filter debris within first few frames of acquisition

---

## Performance Considerations

1. **Object Limit**: Maximum 300 objects per frame to prevent UI lag
2. **Mask Limit**: Maximum 100 masks encoded (masks are expensive)
3. **Image Encoding**: JPEG quality 80% for reasonable file size
4. **Polling Rate**: 50ms between MQTT message checks

---

## Testing

1. Start an acquisition with "Live Segmentation" enabled
2. Verify objects appear with colored overlays
3. Test overlay modes: bbox, mask, both
4. Adjust minimum size and verify small objects are filtered
5. Enable "Remove Static" and verify debris is filtered after 3 frames
6. Check focus indicator accuracy against actual image blur

---

## Dependencies

No new dependencies required. Uses existing:
- OpenCV (cv2)
- NumPy
- PIL/Pillow
- scikit-image (skimage.measure)
- MQTT (paho-mqtt via planktoscope.mqtt)
