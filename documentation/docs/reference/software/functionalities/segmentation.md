# Image Segmentation

This document explains how the PlanktoScope software's *segmenter* program processes raw images (captured by the PlanktoScope's [sample-imaging functionality](./sample-imaging.md)) in order to detect objects - such as plankton, microplastics, and other particles - and to extract each object into its own [segmented image](https://en.wikipedia.org/wiki/Image_segmentation) for downstream use, such as for uploading to EcoTaxa. This document also lists and explains the metadata fields added by the PlanktoScope segmenter for uploading to EcoTaxa.

Currently, the segmenter only operates in batch-processing mode: the segmenter takes as input a complete raw image dataset, and it produces as output a complete segmented object dataset as well as an export archive of segmented objects which can be uploaded to EcoTaxa.

When the segmenter starts, it will perform a *median-calculation* step on the first ten images of the dataset of raw images. The median-calculation step outputs a *median image* which is then used as an input for an *image-correction* step on each raw image; the median image will occasionally be recalculated (conditions triggering a recalculation are described below). Each image-cleaning step outputs a *median-corrected image* is then used as the input for a *mask-calculation* step. Each mask-calculation step outputs a *segmentation mask* which is then used as an input for an *object-extraction* step.

For each raw image from the input dataset, after the object-extraction step outputs a set of objects, the number of extracted objects is accumulated into a [cumulative moving average](https://en.wikipedia.org/wiki/Moving_average#Cumulative_average) of the number of objects extracted per raw image. However, before the cumulative moving average is updated, the number of extracted objects is compared against the previous value of the cumulative moving average (calculated after the previous raw image was processed): if the number of extracted objects is greater than the previous value of the cumulative moving average by more than 20, then the median image will be recalculated for the next raw image. The input for the next median-calculation step will usually be the next 10 consecutive raw images, unless the next raw image is one of the last 10 raw images - in which case the previous ten images will instead be used as the input for the next median-calculation step. Yes, this logic is complicated, and yes, for some reason we don't center the sequence of raw images around the next raw image as our input to the median-calculation step.

## Median-calculation step

The median-calculation step takes as input a sequence of consecutive raw images, but if the image sequence consists of an even number of images then the last image is excluded from the calculation. The median-calculation step uses the raw images to calculate a *median image*, in which the color of each pixel of the output is calculated as the median of the colors of the corresponding pixels in the input images.

The output of this step is supposed to be an estimate of what the the "background" of the image would be if there were no objects within the field-of-view. However, this step is not robust to sample density: if a sample is dense enough that certain pixel locations overlap with objects in more than half of any consecutive sequence of ten images, the color of the "background" in those pixel locations will be estimated as the color of an object in one of those images.

## Image-correction step

The image-correction step takes as input a median image and a raw image. First, the image-correction step divides the color of each pixel of the raw image by the color of the corresponding pixel of the median image; this is probably intended to correct for inhomogeneous illumination in the raw image, and to remove any objects which had been stuck to the flow cell (and thus were included in the median image) from the raw image. Next, the image-correction step slightly [rescales](https://scikit-image.org/docs/0.19.x/api/skimage.exposure.html#skimage.exposure.rescale_intensity) the intensity range of the resulting image (TODO: determine what the effect of this intensity-rescaling operation is - does it make the image brighter or dimmer? Does it increase or decrease the contrast? Does it clip the white value? Why is this step performed???). The final result is a *median-corrected image*.

## Mask-calculation step

The mask-calculation step takes as input a median-corrected image and the result from the previous mask-calculation step. It consists of the following operations:

1. "Simple threshold": this operation applies a [global threshold](https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html#gae8a4a146d1ca78c626a53577199e9c57) to the input corrected image, using the [triangle algorithm](https://bioimagebook.github.io/chapters/2-processing/3-thresholding/thresholding.html#triangle-method) to calculate an optimal threshold value for the image; the output is a mask in which each pixel is set to 0 if the corresponding pixel of the input image is greater than the threshold, and to 255 otherwise. The resulting mask should select for objects which appear darker than the background of the image.

2. "Remove previous mask": this operation combines the result of the previous mask-calculation step with the mask created by the previous "simple threshold" operation, by subtracting the intersection of the two masks from the mask created by the previous "simple threshold" operation. This operation is probably intended to remove objects which had been stuck to the PlanktoScope's flowcell during imaging and thus might appear in many consecutive input corrected images. However, this operation is not robust in dense samples where two different objects might appear in overlapping locations across two consecutive raw images.

3. "Erode": this operation [erodes](https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#gaeb1e0c1033e3f6b891a25d0511362aeb) the mask with a 2-pixel-by-2-pixel square kernel. In the resulting mask, small regions (such as thresholded noise) are eliminated.

4. "Dilate": this operation [dilates](https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c) the mask with an 8-pixel-diameter circular kernel. In the resulting mask, regions remaining after the previous "erode" operation are padded with a margin.

5. "Close": this operation [dilates and then erodes](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html#ga67493776e3ad1a3df63883829375201f) the mask with an 8-pixel-diameter circular kernel. In the resulting mask, small holes in regions remaining after the previous "dilate" operation are eliminated.

6. "Erode2": this operation [erodes](https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#gaeb1e0c1033e3f6b891a25d0511362aeb) the mask with an 8-pixel-diameter circular kernel, inverting the effect of the previous "dilate" operation.

The final result these operations is a spatially-filtered *segmentation mask* where the value of each pixel represents whether that pixel is part of an object or part of the background of the input corrected image.

## Object-extraction step

The object-extraction step takes the following inputs:

- A median-corrected image

- A segmentation mask

- The following sample metadata fields:
  
   - `acq_minimum_mesh`: the diameter of the smallest spherical object which is expected to be in the sample, usually 20 µm. This value is set on the "Fluidic Acquisition" page of the PlanktoScope's Node-RED dashboard as the "Min fraction size" field.
  
   - `process_pixel`: the pixel size calibration of the PlanktoScope, in units of µm per pixel; then the area (in units of µm<sup>2</sup>) per pixel is `process_pixel * process_pixel`. This value is set on the "Hardware Settings" page of the PlanktoScope's Node-RED dashboard as the "Pixel size calibration: um per pixel" field.

First, the object-extraction step calculates a *minimum-area threshold* for objects to extract using the input segmentation mask: the threshold (in units of pixel<sup>2</sup>) is calculated as `pi * (acq_minimum_mesh / 2 / process_pixel) ^ 2`.

Next, the object-extraction step [identifies all connected regions](https://scikit-image.org/docs/0.19.x/api/skimage.measure.html#skimage.measure.label) of the input segmentation mask and [measures properties of those regions](https://scikit-image.org/docs/0.19.x/api/skimage.measure.html#skimage.measure.regionprops). The object-extraction step then discards any region whose filled area (`area_filled` in scikit-image) is less than the minimum-area threshold.

### Metadata calculation

For each resulting region after the minimum-area threshold is applied, that region will be used to extract a segmented and cropped image of the object (including pixels in any holes in the object) from the input median-corrected image. This cropped image is used to calculate some metadata fields about the distribution of colors in the object's segmented image:

- `MeanHue`: the mean of the *hue* channel of the image in a [hue-saturation-value (HSV) representation](https://en.wikipedia.org/wiki/HSL_and_HSV) of the image

- `StdHue`: the standard deviation of the hue channel of the image in an HSV representation of the image

- `MeanSaturation`: the standard deviation of the *saturation* channel of the image in an HSV representation of the image

- `StdSaturation`: the standard deviation of the saturation channel of the image in an HSV representation of the image

- `MeanValue`: the standard deviation of the *value* channel of the image in an HSV representation of the image

- `StdValue`: the standard deviation of the value channel of the image in an HSV representation of the image

Additionally, some metadata for the object is calculated from the [region properties calculated by scikit-image](https://scikit-image.org/docs/0.19.x/api/skimage.measure.html#regionprops) for that object's region:

- `label`: The identifier of the object's region, as assigned by scikit-image. This corresponds to the `label` region property in scikit-image.

- Basic area properties:
  
   - `area_exc`: Number of pixels in the region (excluding pixels in any holes). This corresponds to the `area` region property in scikit-image.
  
   - `area`: Number of pixels of the region with all holes filled in (i.e. including pixels in any holes). This corresponds to the `area_filled` region property in scikit-image. Yes, it's somewhat confusing that the PlanktoScope segmenter renames scikit-image's `area` region property to `area_exc` and renames scikit-image's `area_filled` region property to `area`.
  
   - `%area`: Ratio between the number of pixels in any holes in the region and the total number of pixels of the region with all holes filled in; calculated as `1 - area_exc / area`. In other words, this represents the proportion of the region which consists of holes. Yes, `%area` is a misleading name both because of the `%` in the name and because of the `area` in the name.

- Equivalent-circle properties:
  
   - `equivalent_diameter`: The diameter (in pixels) of a circle with the same number of pixels in its area as the number of pixels in the region (excluding pixels in any holes). This corresponds to the `equivalent_diameter_area` property in scikit-image.
- Equivalent-ellipse properties:
   - `eccentricity`: Eccentricity of the ellipse that has the same second-moments as the region; eccentricity is the ratio of the focal distance (distance between focal points) over the major axis length. The value is in the interval [0, 1), where a value of 0 represents a circle. This corresponds to the `eccentricity` property in scikit-image.
  
   - `major`: The length (in pixels) of the major axis of region's equivalent ellipse. This corresponds to the `axis_major_length` property in scikit-image.
  
   - `minor`: The length (in pixels) of the minor axis of the region's equivalent ellipse. This corresponds to the `axis_minor_length` property in scikit-image.
  
   - `elongation`: The ratio between `major` and `minor`.
  
   - `angle`: Angle (in degrees) between the x-axis of the input median-corrected image and the major axis of the region's equivalent ellipse. Values range from 0 deg to 180 deg counter-clockwise. This is calculated from the `orientation` property in scikit-image.

- Equivalent-object perimeter properties:
  
   - `perim.`: Perimeter (in pixels) of an object which approximates the region's contour as a line through the centers of border pixels using a 4-connectivity. This corresponds to the `perimeter` property in scikit-image.
  
   - `perimareaexc`: Ratio between the perimeter and the number of pixels in the region (excluding pixels in any holes). Calculated as `perim. / area_exc`.
  
   - `perimmajor`: Ratio between the perimeter and the length of the major axis of the region's equivalent ellipse. Calculated as `perim. / major`.
  
   - `circ.`: The [roundness](https://en.wikipedia.org/wiki/Roundness#Roundness_error_definitions) of the region's equivalent object, including pixels in any holes. Calculated as `4 * π * area / (perim. * perim.)`. Ranges from 1 for a perfect circle to 0 for highly non-circular shapes.
  
   - `circex`: The roundness of the region's equivalent object, excluding pixels in any holes. Calculated as `4 * π * area_exc / (perim. * perim.)`. Ranges from 1 for a perfect circle to 0 for highly non-circular shapes or shapes with many large holes.

- Bounding box (the smallest rectangle which includes all pixels of the region, under the constraint that the edges of the box are parallel to the x- and y-axes of the input median-corrected image) properties:
  
   - `bx`: x-position (in pixels) of the top-left corner of the region's bounding box, relative to the top-left corner of the input median-corrected image. This corresponds to the second element of the `bbox` property in scikit-image.
  
   - `by`: y-position (in pixels) of the top-left corner of the region's bounding box, relative to the top-left corner of the input median-corrected image. This corresponds to the first element of the `bbox` property in scikit-image.
  
   - `width`: Width (in number of pixels) of the region's bounding box. This is calculated from the elements of the `bbox` property in scikit-image.
  
   - `height`: Height (in number of pixels) of the region's bounding box. This is calculated from the elements of the `bbox` property in scikit-image.
  
   - `bounding_box_area`: Number of pixels in the region's bounding box; equivalent to `width * height`. This corresponds to the `area_bbox` region property in scikit-image.
  
   - `extent`: Ratio between the number of pixels in the region (excluding pixels in any holes) and the number of pixels in the region's bounding box; equivalent to `area_exc / bounding_box_area`. This corresponds to the `extent` region property in scikit-image.

- Convex hull (the smallest convex polygon which encloses the region) properties:
  
   - `convex_area`: Number of pixels in the convex hull of the region. This corresponds to the `area_convex` region property in scikit-image.
  
   - `solidity`: Ratio between the number of pixels in the region (excluding pixels in any holes) and the number of pixels in the convex hull of the region. Equivalent to `area_exc / convex_area`. This corresponds to the `solidity` region property in scikit-image.

- Unweighted centroid properties:
  
   - `x`: x-position (in pixels) of the centroid of the object, relative to the top-left corner of the input median-corrected image. This corresponds to the second element of the `centroid` region property in scikit-image.
  
   - `y`: y-position (in pixels) of the centroid of the object, relative to the top-left corner of the input median-corrected image. This corresponds to the first element of the `centroid` region property in scikit-image.
  
   - `local_centroid_col`: x-position (in pixels) of the centroid of the object, relative to the top-left corner of the region's bounding box; equivalent to `x - bx`. This corresponds to the second element of the `centroid_local` region property in scikit-image.
  
   - `local_centroid_row`: y-position (in pixels) of the centroid of the object, relative to the top-left corner of the region's bounding box; equivalent to `y - by`. This corresponds to the first element of the `centroid_local` region property in scikit-image.

- Topological properties:
  
   - `euler_number`: The [Euler characteristic](https://en.wikipedia.org/wiki/Euler_characteristic) of the set of non-zero pixels. Computed as the number of connected components subtracted by the number of holes (with 2-connectivity). This corresponds to the `euler_number` property in scikit-image.

### Output image cropping

Finally, a segmented and cropped image of the object (including pixels in any holes in the object) is saved from the input median-corrected image, but with the crop expanded by up to 10 pixels in each direction (TODO: check whether this description is accurate - the corresponding code is extremely unreadable).

Thus, the output of the output-extraction step is a set of objects, each with a corresponding cropped image saved to file and with a corresponding list of metadata values.
