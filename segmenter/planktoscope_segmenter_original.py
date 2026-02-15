#!/usr/bin/env python3
"""
planktoscope_segmenter_original.py - PlanktoScope Segmentation Pipeline

This implements the exact PlanktoScope segmentation pipeline from the main codebase:
- Simple threshold (THRESH_BINARY_INV + THRESH_TRIANGLE, init=127)
- Erode (2x2 rect kernel)
- Dilate (8x8 ellipse kernel)
- Close (8x8 ellipse kernel)
- Erode2 (8x8 ellipse kernel)
- skimage.measure.label + regionprops for object detection and feature extraction
- HSV color statistics matching the main branch

This matches the segmenter from:
https://github.com/PlanktoScope/PlanktoScope/tree/main/segmenter

Copyright follows the original PlanktoScope GPL v3 license.
"""

import time

import cv2
import numpy as np
import skimage.measure

try:
    from loguru import logger
except ImportError:
    class SimpleLogger:
        def debug(self, msg): pass
        def info(self, msg): print(f"INFO: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    logger = SimpleLogger()


class PlanktoScopeOriginalSegmenter:
    """PlanktoScope segmentation pipeline matching the main codebase exactly."""

    def __init__(self):
        self.previous_mask = None

    def reset(self):
        """Reset the previous mask for a new acquisition."""
        self.previous_mask = None

    # ── Threshold operations ──────────────────────────────────────────

    def simple_threshold(self, img):
        """Apply simple threshold using TRIANGLE method.

        Matches operations.simple_threshold() from the main codebase.
        """
        logger.debug("Simple threshold calc")
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(
            img_gray, 127, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_TRIANGLE
        )
        logger.info(f"Threshold value used was {ret}")
        logger.success("Simple threshold is done")
        return mask

    # ── Morphological operations ──────────────────────────────────────

    def erode(self, mask):
        """Erode with 2x2 rectangular kernel."""
        logger.info("Erode calc")
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        mask_erode = cv2.erode(mask, kernel)
        logger.success("Erode calc")
        return mask_erode

    def dilate(self, mask):
        """Dilate with 8x8 elliptical kernel."""
        logger.info("Dilate calc")
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
        mask_dilate = cv2.dilate(mask, kernel)
        logger.success("Dilate calc")
        return mask_dilate

    def close(self, mask):
        """Close operation with 8x8 elliptical kernel."""
        logger.info("Close calc")
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
        mask_close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        logger.success("Close calc")
        return mask_close

    def erode2(self, mask):
        """Second erode with 8x8 elliptical kernel."""
        logger.info("Erode calc 2")
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
        mask_erode_2 = cv2.erode(mask, kernel)
        logger.success("Erode calc 2")
        return mask_erode_2

    def remove_previous_mask(self, mask):
        """Remove objects from previous frame (stuck particles).

        Matches operations.remove_previous_mask() from the main codebase.
        """
        if self.previous_mask is not None:
            mask_and = mask & self.previous_mask
            mask_final = mask - mask_and
            logger.success("Done removing the previous mask")
            self.previous_mask = mask
            return mask_final
        else:
            logger.debug("First mask")
            self.previous_mask = mask
            return self.previous_mask

    # ── Mask creation pipeline ────────────────────────────────────────

    def _create_mask(self, img, remove_previous=False):
        """Create binary mask using the exact PlanktoScope pipeline.

        Pipeline:
        1. simple_threshold (TRIANGLE)
        2. remove_previous_mask or no_op
        3. erode (2x2 rect)
        4. dilate (8x8 ellipse)
        5. close (8x8 ellipse)
        6. erode2 (8x8 ellipse)
        """
        logger.info("Starting the mask creation")

        # Step 1: Simple threshold
        mask = self.simple_threshold(img)

        # Step 2: Remove previous mask (for stuck particle removal)
        if remove_previous:
            mask = self.remove_previous_mask(mask)

        # Step 3-6: Morphological operations
        mask = self.erode(mask)
        mask = self.dilate(mask)
        mask = self.close(mask)
        mask = self.erode2(mask)

        logger.success("Mask created")
        return mask

    # ── Feature extraction (matching main codebase) ───────────────────

    def _get_color_info(self, bgr_img, mask):
        """Extract HSV color statistics.

        Matches _get_color_info() from the main codebase exactly.
        Uses np.mean/std with where= parameter on boolean mask.
        """
        hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
        (h_channel, s_channel, v_channel) = cv2.split(hsv_img)
        h_mean = np.mean(h_channel, where=mask)
        s_mean = np.mean(s_channel, where=mask)
        v_mean = np.mean(v_channel, where=mask)
        h_stddev = np.std(h_channel, where=mask)
        s_stddev = np.std(s_channel, where=mask)
        v_stddev = np.std(v_channel, where=mask)
        return {
            "MeanHue": h_mean,
            "MeanSaturation": s_mean,
            "MeanValue": v_mean,
            "StdHue": h_stddev,
            "StdSaturation": s_stddev,
            "StdValue": v_stddev,
        }

    def _extract_metadata_from_regionprop(self, prop):
        """Extract metadata from a regionprop object.

        Matches _extract_metadata_from_regionprop() from the main codebase exactly.
        """
        return {
            "label": prop.label,
            "width": prop.bbox[3] - prop.bbox[1],
            "height": prop.bbox[2] - prop.bbox[0],
            "bx": prop.bbox[1],
            "by": prop.bbox[0],
            "circ.": (4 * np.pi * prop.filled_area) / prop.perimeter ** 2,
            "area_exc": prop.area,
            "area": prop.filled_area,
            "%area": 1 - (prop.area / prop.filled_area),
            "major": prop.major_axis_length,
            "minor": prop.minor_axis_length,
            "y": prop.centroid[0],
            "x": prop.centroid[1],
            "convex_area": prop.convex_area,
            "perim.": prop.perimeter,
            "elongation": np.divide(prop.major_axis_length, prop.minor_axis_length),
            "perimareaexc": prop.perimeter / prop.area,
            "perimmajor": prop.perimeter / prop.major_axis_length,
            "circex": np.divide(4 * np.pi * prop.area, prop.perimeter ** 2),
            "angle": prop.orientation / np.pi * 180 + 90,
            "bounding_box_area": prop.bbox_area,
            "eccentricity": prop.eccentricity,
            "equivalent_diameter": prop.equivalent_diameter,
            "euler_number": prop.euler_number,
            "extent": prop.extent,
            "local_centroid_col": prop.local_centroid[1],
            "local_centroid_row": prop.local_centroid[0],
            "solidity": prop.solidity,
        }

    # ── Object slicing (matching main codebase) ──────────────────────

    @staticmethod
    def _augment_slice(dim_slice, max_dims, size=10):
        """Expand a slice by `size` pixels in all directions.

        Matches __augment_slice() from the main codebase.
        """
        dim_slice = list(dim_slice)
        for i in range(2):
            if dim_slice[i].start < size:
                dim_slice[i] = slice(0, dim_slice[i].stop)
            else:
                dim_slice[i] = slice(dim_slice[i].start - size, dim_slice[i].stop)

        for i in range(2):
            if dim_slice[i].stop + size == max_dims[i]:
                dim_slice[i] = slice(dim_slice[i].start, max_dims[i])
            else:
                dim_slice[i] = slice(dim_slice[i].start, dim_slice[i].stop + size)

        return tuple(dim_slice)

    # ── Main entry point ──────────────────────────────────────────────

    def segment_and_extract(self, image_path, params=None, img=None):
        """Run the full PlanktoScope segmentation pipeline.

        Matches the _pipe() + _slice_image() logic from the main codebase.

        Args:
            image_path: Path to input image
            params: Optional parameters dict with:
                - min_diameter: Minimum equivalent diameter in µm (default 20)
                  This corresponds to process_min_ESD in the main codebase.
                - pixel_size: µm per pixel (default 0.94)
                - remove_previous: Whether to subtract previous mask (default False)
            img: Optional pre-loaded image (e.g. after flat-field correction)

        Returns:
            dict with status, objects list, timing info
        """
        if params is None:
            params = {}

        min_diameter = params.get("min_diameter", 20)
        pixel_size = params.get("pixel_size", 0.94)
        remove_previous = params.get("remove_previous", False)

        start_time = time.time()

        # Load image if not provided
        if img is None:
            img = cv2.imread(image_path)
        if img is None:
            return {"status": "error", "error": f"Could not load image: {image_path}"}

        # Step 1-6: Create mask using the exact PlanktoScope pipeline
        mask = self._create_mask(img, remove_previous=remove_previous)

        # Step 7: Label connected components and extract regionprops
        # This matches the main codebase's _slice_image() method
        labels, nlabels = skimage.measure.label(mask, return_num=True)
        regionprops = skimage.measure.regionprops(labels)

        # Filter by equivalent diameter (matching process_min_ESD)
        regionprops_filtered = [
            region
            for region in regionprops
            if region.equivalent_diameter_area >= min_diameter
        ]
        object_number = len(regionprops_filtered)
        logger.debug(f"Found {nlabels} labels, or {object_number} after size filtering")

        # Step 8: Extract objects with metadata and color info
        objects = []
        for i, region in enumerate(regionprops_filtered):
            region.label = i

            # Extract metadata from regionprop (matching main codebase)
            metadata = self._extract_metadata_from_regionprop(region)

            # Extract color info from the object's bounding box
            obj_image = img[region.slice]
            colors = self._get_color_info(obj_image, region.filled_image)

            # Get expanded slice for crop saving (10px padding)
            expanded_slice = self._augment_slice(region.slice, labels.shape, 10)

            # Build bbox from region
            bx = region.bbox[1]  # column start
            by = region.bbox[0]  # row start
            w = region.bbox[3] - region.bbox[1]
            h = region.bbox[2] - region.bbox[0]

            diameter_um = region.equivalent_diameter * pixel_size

            obj = {
                "id": i + 1,
                "bbox": {"x": bx, "y": by, "width": w, "height": h},
                "expanded_slice": expanded_slice,
                "diameter_um": diameter_um,
                "area_px": region.area,
                "features": {**metadata, **colors},
                "method": "planktoscope",
            }
            objects.append(obj)

        process_time = int((time.time() - start_time) * 1000)

        return {
            "status": "success",
            "objects": objects,
            "objects_found": object_number,
            "processing_time_ms": process_time,
            "method": "planktoscope",
            "mask": mask,
        }


# Singleton instance for use in segment_live.py
segmenter = PlanktoScopeOriginalSegmenter()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python planktoscope_segmenter_original.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    params = {
        "min_diameter": 20,
        "pixel_size": 0.94,
    }

    result = segmenter.segment_and_extract(image_path, params)
    # Remove non-serializable fields for JSON output
    if "mask" in result:
        del result["mask"]
    for obj in result.get("objects", []):
        if "expanded_slice" in obj:
            del obj["expanded_slice"]
    print(json.dumps(result, indent=2, default=str))
