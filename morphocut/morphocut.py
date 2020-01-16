"""Experiment on processing KOSMOS data using MorphoCut."""

import datetime
import os

from skimage.util import img_as_ubyte

from morphocut import Call
from morphocut.contrib.ecotaxa import EcotaxaWriter
from morphocut.contrib.zooprocess import CalculateZooProcessFeatures
from morphocut.core import Pipeline
from morphocut.file import Find
from morphocut.image import (
    ExtractROI,
    FindRegions,
    ImageReader,
    ImageWriter,
    RescaleIntensity,
    RGB2Gray,
)
from morphocut.stat import RunningMedian
from morphocut.str import Format
from morphocut.stream import TQDM, Enumerate

# import_path = "/data-ssd/mschroeder/Datasets/Pyrocystis_noctiluca/RAW"
import_path = "/home/pi/Desktop/PlanktonScope_acquisition/01_16_2020/afternoon/14_1"
export_path = "/home/pi/Desktop/PlanktonScope_acquisition/01_16_2020/14_1_export"
archive_fn = os.path.join(export_path, "14_1_morphocut_processed.zip")

# Meta data that is added to every object
global_metadata = {
    "acq_instrument": "Planktoscope",
    "process_datetime": datetime.datetime.now(),
}

if __name__ == "__main__":
    print("Processing images under {}...".format(import_path))

    # Create export_path in case it doesn't exist
    os.makedirs(export_path, exist_ok=True)

    # Define processing pipeline
    with Pipeline() as p:
        # Recursively find .jpg files in import_path.
        # Sort to get consective frames.
        abs_path = Find(import_path, [".jpg"], sort=True, verbose=True)

        # Extract name from abs_path
        name = Call(lambda p: os.path.splitext(os.path.basename(p))[0], abs_path)

        # Read image
        img = ImageReader(abs_path)

        # Apply running median to approximate the background image
        flat_field = RunningMedian(img, 10)

        # Correct image
        img = img / flat_field

        # Rescale intensities and convert to uint8 to speed up calculations
        img = RescaleIntensity(img, in_range=(0, 1.1), dtype="uint8")

        # Show progress bar for frames
        TQDM(Format("Frame {name}", name=name))

        # Convert image to uint8 gray
        img_gray = RGB2Gray(img)
        img_gray = Call(img_as_ubyte, img_gray)

        # Apply threshold find objects
        threshold = 204  # Call(skimage.filters.threshold_otsu, img_gray)
        mask = img_gray < threshold

        # Write corrected frames
        frame_fn = Format(os.path.join(export_path, "{name}.jpg"), name=name)
        ImageWriter(frame_fn, img)

        # Find objects
        regionprops = FindRegions(
            mask, img_gray, min_area=100, padding=10, warn_empty=name
        )

        # For an object, extract a vignette/ROI from the image
        roi_orig = ExtractROI(img, regionprops, bg_color=255)
        roi_gray = ExtractROI(img_gray, regionprops, bg_color=255)

        # Generate an object identifier
        i = Enumerate()
        object_id = Format("{name}_{i:d}", name=name, i=i)

        # Calculate features. The calculated features are added to the global_metadata.
        # Returns a Variable representing a dict for every object in the stream.
        meta = CalculateZooProcessFeatures(
            regionprops, prefix="object_", meta=global_metadata
        )
        # If CalculateZooProcessFeatures is not used, we need to copy global_metadata into the stream:
        # meta = Call(lambda: global_metadata.copy())
        # https://github.com/morphocut/morphocut/issues/51

        # Add object_id to the metadata dictionary
        meta["object_id"] = object_id

        # Generate object filenames
        orig_fn = Format("{object_id}.jpg", object_id=object_id)
        gray_fn = Format("{object_id}-gray.jpg", object_id=object_id)

        # Write objects to an EcoTaxa archive:
        # roi image in original color, roi image in grayscale, metadata associated with each object
        EcotaxaWriter(archive_fn, [(orig_fn, roi_orig), (gray_fn, roi_gray)], meta)

        # Progress bar for objects
        TQDM(Format("Object {object_id}", object_id=object_id))

    # Execute pipeline
    p.run()

