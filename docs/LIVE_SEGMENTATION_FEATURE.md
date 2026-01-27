# Live Segmentation with Real-time Preview and Blur Metrics

## Summary

This PR introduces **real-time segmentation preview** during image acquisition, allowing operators to see detected plankton objects as they are captured. It also adds **per-object blur metrics** for quality assessment and includes critical bug fixes for acquisition timing and calibration consistency.

---

## New Features

### Real-time Segmentation Preview

Enable live object detection directly from the Acquisition page. As images are captured, detected objects are immediately highlighted with configurable overlays.

![Live Segmentation Preview Toggle](docs/images/Preview.jpg)
*The Live Segmentation Preview panel appears below the acquisition controls. Toggle it on to enable real-time detection.*

---

### Overlay Mode Selection

Choose how detected objects are visualized during acquisition:

| Mode | Description |
|------|-------------|
| **Bounding Boxes** | Cyan rectangles around each detected object |
| **Masks** | Semi-transparent overlay showing exact object boundaries |
| **Both** | Combined bounding boxes and masks |

![Overlay Mode Dropdown](docs/images/choice.jpg)
*Select between Bounding Boxes, Masks, or Both to customize the visualization.*

---

### Configurable Detection Parameters

Fine-tune detection directly from the toolbar:

![Live Segmentation Toolbar](docs/images/Toggle..jpg)

| Control | Description |
|---------|-------------|
| **Min Size (um)** | Filter out objects smaller than this diameter (ESD) |
| **Remove Static** | Automatically filter debris stuck on the flow cell glass |
| **Objects** | Live count of detected objects in current frame |
| **Focus** | Real-time focus quality indicator |

---

### Real-time Focus Quality Indicator

Monitor image sharpness during acquisition with the live blur metric display. The system uses Laplacian variance to quantify focus quality:

#### Good Focus (Score > 50)
![Good Focus Example](docs/images/good.jpg)
*Sharp image with clear object boundaries. Focus score of 41 indicates acceptable quality.*

#### Poor Focus (Score < 25)
![Poor Focus Example](docs/images/poor.jpg)
*Blurry image requiring focus adjustment. Focus score of 3 indicates poor quality.*

| Score Range | Status | Indicator |
|-------------|--------|-----------|
| > 50 | Good | Green |
| 25-50 | OK | Yellow |
| < 25 | Poor | Red |

**Note:** Per-object blur metrics are also saved to the EcoTaxa `.tsv` file as `object_blur_laplacian`, enabling post-acquisition quality sorting.

---

## Bug Fixes

### Fix #1: Pump Timing Synchronization

**Problem:** The pump was running continuously instead of following the proper acquisition sequence (pump → wait 0.5s → capture → repeat), causing motion blur.

**Root Cause:** The MQTT progress message (`{"type": "progress", ...}`) that signals image capture completion was removed during a refactor, breaking the synchronization between the imager and live segmenter.

**Solution:** Restored the progress message in `controller/imager/mqtt.py`.

---

### Fix #2: Pixel Size Calibration Consistency

**Problem:** Live segmentation used a hardcoded pixel size (0.75 µm/pixel) instead of reading from the calibration dashboard, causing inconsistent object size filtering.

**Solution:** Live segmenter now reads `process_pixel_fixed` from `/home/pi/PlanktoScope/hardware.json` to match the calibration set in the dashboard.

---

## Technical Details

### Files Changed

| File | Change |
|------|--------|
| `controller/imager/mqtt.py` | Restored progress MQTT message |
| `segmenter/planktoscope/segmenter/live.py` | Load pixel size from hardware config |
| `LIVE_SEGMENTATION_CHANGES.md` | Updated documentation |
| `BUGFIX_CHANGELOG.md` | Added fix documentation |
| `CHANGELOG_PR_DOCUMENTATION.md` | Updated feature documentation |

### MQTT Topics

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `segmenter/live` | Frontend → Backend | Start/stop live segmentation |
| `status/segmenter/live` | Backend → Frontend | Object detection results |
| `status/imager` | Imager → Segmenter | Image capture progress |

---

## Testing Checklist

- [ ] Enable live segmentation on Acquisition page
- [ ] Start acquisition and verify objects appear with overlays
- [ ] Test all overlay modes: bounding boxes, masks, both
- [ ] Adjust minimum size filter, verify small objects filtered
- [ ] Enable "Remove Static" and verify debris is filtered
- [ ] Check focus indicator accuracy against actual image blur
- [ ] Verify pixel size matches calibration dashboard setting
- [ ] Confirm proper pump timing (no continuous pumping)

---

## Deployment

```bash
# Frontend (after npm run build)
scp -r frontend/dist/* pi@planktoscope.local:/home/pi/PlanktoScope/frontend/dist/

# Backend
scp segmenter/planktoscope/segmenter/live.py pi@planktoscope.local:/home/pi/PlanktoScope/segmenter/planktoscope/segmenter/
scp controller/imager/mqtt.py pi@planktoscope.local:/home/pi/PlanktoScope/controller/imager/

# Restart services
ssh pi@planktoscope.local "sudo systemctl restart segmenter imager"
```

---

## Related Issues

- Fixes continuous pump running during acquisition
- Fixes inconsistent object filtering between live and batch segmentation
