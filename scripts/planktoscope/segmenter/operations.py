# Logger library compatible with multiprocessing
from loguru import logger

import cv2

__mask_to_remove = None


def adaptative_threshold(img):
    """Apply a threshold to a color image to get a mask from it
    Uses an adaptative threshold with a blocksize of 19 and reduction of 4.

    Args:
        img (cv2 img): Image to extract the mask from

    Returns:
        cv2 img: binary mask
    """
    # start = time.monotonic()
    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    logger.debug("Adaptative threshold calc")
    # img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, mask = cv2.threshold(img_gray, 127, 200, cv2.THRESH_OTSU)
    mask = cv2.adaptiveThreshold(
        img_gray,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=19,  # must be odd
        C=4,
    )
    # mask = 255 - img_tmaskhres

    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # logger.debug(time.monotonic() - start)
    # logger.success(f"Threshold used was {ret}")
    logger.success(f"Adaptative threshold is done")
    return mask


def simple_threshold(img):
    """Apply a threshold to a color image to get a mask from it

    Args:
        img (cv2 img): Image to extract the mask from

    Returns:
        cv2 img: binary mask
    """
    # start = time.monotonic()
    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    logger.debug("Simple threshold calc")
    # img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(
        img_gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_TRIANGLE
    )

    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # logger.debug(time.monotonic() - start)
    logger.info(f"Threshold value used was {ret}")
    logger.success(f"Simple threshold is done")
    return mask


def erode(mask):
    """Erode the given mask with a rectangular kernel of 2x2

    Args:
        mask (cv2 img): mask to erode

    Returns:
        cv2 img: binary mask after transformation
    """
    logger.info("Erode calc")
    # start = time.monotonic()
    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    mask_erode = cv2.erode(mask, kernel)

    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # logger.debug(time.monotonic() - start)
    logger.success("Erode calc")
    return mask_erode


def dilate(mask):
    """Apply a dilate operation to the given mask, with an elliptic kernel of 8x8

    Args:
        mask (cv2 img): mask to apply the operation on

    Returns:
        cv2 img: mask after the transformation
    """
    logger.info("Dilate calc")
    # start = time.monotonic()
    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
    mask_dilate = cv2.dilate(mask, kernel)

    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # logger.debug(time.monotonic() - start)
    logger.success("Dilate calc")
    return mask_dilate


def close(mask):
    """Apply a close operation to the given mask, with an elliptic kernel of 8x8

    Args:
        mask (cv2 img): mask to apply the operation on

    Returns:
        cv2 img: mask after the transformation
    """
    logger.info("Close calc")
    # start = time.monotonic()
    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
    mask_close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # logger.debug(time.monotonic() - start)
    logger.success("Close calc")
    return mask_close


def erode2(mask):
    """Apply an erode operation to the given mask, with an elliptic kernel of 8x8

    Args:
        mask (cv2 img): mask to apply the operation on

    Returns:
        cv2 img: mask after the transformation
    """
    logger.info("Erode calc 2")
    # start = time.monotonic()
    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
    mask_erode_2 = cv2.erode(mask, kernel)

    # logger.debug(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # logger.debug(time.monotonic() - start)
    logger.success("Erode calc 2")
    return mask_erode_2


def remove_previous_mask(mask):
    """Remove the mask from the previous pass from the given mask
    The given mask is then saved to be applied to the next pass

    Args:
        mask (cv2 img): mask to apply the operation on

    Returns:
        cv2 img: mask after the transformation
    """
    global __mask_to_remove
    if __mask_to_remove is not None:
        # start = time.monotonic()
        # np.append(__mask_to_remove, img_erode_2)
        # logger.debug(time.monotonic() - start)
        mask_and = mask & __mask_to_remove
        mask_final = mask - mask_and
        logger.success("Done removing the previous mask")
        __mask_to_remove = mask
        return mask_final
    else:
        logger.debug("First mask")
        __mask_to_remove = mask
        return __mask_to_remove


def reset_previous_mask():
    """Remove the mask from the previous pass from the given mask
    The given mask is then saved to be applied to the next pass

    Args:
        mask (cv2 img): mask to apply the operation on

    Returns:
        cv2 img: mask after the transformation
    """
    global __mask_to_remove
    __mask_to_remove = None
