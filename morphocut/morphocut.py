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

from skimage.feature import canny
from skimage.color import rgb2gray, label2rgb
from skimage.morphology import disk
from skimage.morphology import erosion, dilation, closing
from skimage.measure import label, regionprops


import_path = "/media/tpollina/rootfs/home/pi/Desktop/PlanktonScope_acquisition/01_17_2020/RAW"
export_path = "/media/tpollina/rootfs/home/pi/Desktop/PlanktonScope_acquisition/01_17_2020/"
CLEAN = os.path.join(export_path, "CLEAN")
os.makedirs(CLEAN, exist_ok=True)


OBJECTS = os.path.join(export_path, "OBJECTS")
os.makedirs(OBJECTS, exist_ok=True)

archive_fn = os.path.join(export_path, "ecotaxa_export.zip")

# Meta data that is added to every object
global_metadata = {
    "acq_instrument": "Planktoscope",
    "process_datetime": datetime.datetime.now(),
    "sample_project": "PlanktonScope Villefranche",
    "sample_ship": "Kayak de Fabien",
    "sample_operator": "Thibaut Pollina",
    "sample_id": "Flowcam_PlanktonScope_comparison",
    "sample_sampling_gear": "net",
    "sample_time":150000,
    "sample_date":16112020,
    "object_lat": 43.696146,
    "object_lon": 7.308359,
    "acq_fnumber_objective": 16,
    "acq_celltype": 200,
    "process_pixel": 1.19,
    "acq_camera": "Pi Camera V2.1",
    "acq_instrument": "PlanktonScope V2.1",
    "acq_software": "Node-RED Dashboard and raw python",
    "acq_instrument_ID": "copepode",
    "acq_volume": 24,
    "acq_flowrate": "Unknown",
    "acq_camera.resolution" : "(3280, 2464)",
    "acq_camera.iso" : 60,
    "acq_camera.shutter_speed" : 100,
    "acq_camera.exposure_mode" : 'off',
    "acq_camera.awb_mode" : 'off',
    "acq_nb_frames" : 1000
}

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

    # Convert image to uint8 gray
    img_gray = RGB2Gray(img)

    img_gray = Call(img_as_ubyte, img_gray)

    img_canny = Call(canny, img_gray, sigma=0.3)

    img_dilate = Call(dilation, img_canny)

    img_closing = Call(closing, img_dilate)

    mask = Call(erosion, img_closing)

    # Show progress bar for frames
    TQDM(Format("Frame {name}", name=name))
    
    # Apply threshold find objects
    #threshold = 204  # Call(skimage.filters.threshold_otsu, img_gray)
    #mask = img_gray < threshold

    # Write corrected frames
    frame_fn = Format(os.path.join(CLEAN, "{name}.jpg"), name=name)
    ImageWriter(frame_fn, img)

    # Find objects
    regionprops = FindRegions(
        mask, img_gray, min_area=1000, padding=10, warn_empty=name
    )

    # For an object, extract a vignette/ROI from the image
    roi_orig = ExtractROI(img, regionprops, bg_color=255)

    roi_orig
    # Generate an object identifier
    i = Enumerate()
    #Call(print,i)

    object_id = Format("{name}_{i:d}", name=name, i=i)
    #Call(print,object_id)
    
    object_fn = Format(os.path.join(OBJECTS, "{name}.jpg"), name=object_id)
    ImageWriter(object_fn, roi_orig)


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

    # Write objects to an EcoTaxa archive:
    # roi image in original color, roi image in grayscale, metadata associated with each object
    EcotaxaWriter(archive_fn, (orig_fn, roi_orig), meta)

    # Progress bar for objects
    TQDM(Format("Object {object_id}", object_id=object_id))


import datetime

BEGIN = datetime.datetime.now()
# Execute pipeline
p.run() 

END = datetime.datetime.now()

print("MORPHOCUT    :"+str(END-BEGIN))
