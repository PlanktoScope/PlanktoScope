
import datetime
import os

from skimage.util import img_as_ubyte
from skimage.filters import threshold_otsu


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

import_path = "/home/pi/Desktop/PlanktonScope_acquisition/01_17_2020/16_2"
export_path = "/home/pi/Desktop/PlanktonScope_acquisition/01_17_2020/16"
archive_fn = os.path.join(export_path, "17_morphocut_processed.zip")

# Meta data that is added to every object
global_metadata = {
    "process_datetime": datetime.datetime.now(),
    "sample_project": "PlanktonScope Villefranche",
    "sample_ship": "Kayak de Fabien",
    "sample_operator": "Thibaut Pollina",
    "sample_id": "Flowcam_PlanktonScope_comparison",
    "sample_sampling_gear": "net",
    "object_date": 20200117,
    "object_time": 150000,
    "object_lat": 43.696146,
    "object_lon": 7.308359,
    "object_depth_min": 0,
    "object_depth_max": 1,
    "acq_fnumber_objective": 16,
    "acq_celltype": 400,
    "acq_camera": "Pi Camera V2.1",
    "acq_instrument": "PlanktonScope V2.1",
    "acq_software": "Node-RED Dashboard and raw python",
    "acq_instrument_ID": "copepode",
    "acq_camera_resolution" : "(3280, 2464)",
    "acq_camera_iso" : 60,
    "acq_camera_shutter_speed" : 100,
    "acq_camera_exposure_mode" : "off",
    "acq_camera_awb_mode" : "off",
    "process_pixel": 1.19

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

        # Show progress bar for frames
        TQDM(Format("Frame {name}", name=name))
        
        # Read image
        img = ImageReader(abs_path)
        

        # Convert image to uint8 gray
        img_gray = RGB2Gray(img)
        
        #img_gray = Call(img_as_ubyte, img_gray)

        # Apply threshold find objects
        
        #threshold = 200  #
        #threshold = Call(threshold_otsu, img_gray)
        threshold = 180  #
        
        mask = img_gray < threshold
        
        
        # Write corrected frames
        
        ImageWriter(frame_fn, mask)

        # Find objects
        regionprops = FindRegions(
            mask, img_gray, min_area=300, padding=10, warn_empty=name
        )

        # For an object, extract a vignette/ROI from the image
        roi_orig = ExtractROI(img, regionprops, bg_color=255)
        #roi_gray = ExtractROI(img_gray, regionprops, bg_color=255)

        # Generate an object identifier
        i = Enumerate()
        
        object_id = Format("{name}_{i:d}", name=name, i=i)

        # Calculate features. The calculated features are added to the global_metadata.
        # Returns a Variable representing a dict for every object in the stream.
        #meta = CalculateZooProcessFeatures(
        #    regionprops, prefix="object_", meta=global_metadata
        #)
        # If CalculateZooProcessFeatures is not used, we need to copy global_metadata into the stream:
        # meta = Call(lambda: global_metadata.copy())
        # https://github.com/morphocut/morphocut/issues/51

        # Add object_id to the metadata dictionary
        #meta["object_id"] = object_id

        # Generate object filenames
        
        orig_fn = Format(os.path.join(export_path, "{object_id}.jpg"), object_id=object_id)
        #gray_fn = Format("{object_id}-gray.jpg", object_id=object_id)

        ImageWriter(orig_fn, roi_orig)

        # Write objects to an EcoTaxa archive:
        # roi image in original color, roi image in grayscale, metadata associated with each object
        #EcotaxaWriter(archive_fn, [(orig_fn, roi_orig)], meta)

        # Progress bar for objects
        TQDM(Format("Object {object_id}", object_id=object_id))

    # Execute pipeline
    p.run()
