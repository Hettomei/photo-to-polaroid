"""
convert to polaroid
Thanks to https://raw.githubusercontent.com/thegaragelab/pythonutils/master/polaroid/polaroid.py
"""

import sys
import logging
from os import path

from PIL import Image, ImageDraw

# Real kodak mini proportion
# IMAGE_TOP = 140
# IMAGE_BOTTOM = 280
# IMAGE_LEFT = 70
# IMAGE_RIGHT = IMAGE_LEFT

IMAGE_TOP = 100
IMAGE_BOTTOM = 200
IMAGE_LEFT = 70
IMAGE_RIGHT = IMAGE_LEFT

BORDER_SIZE = 1

COLOR_FRAME = (255, 255, 255)
COLOR_BORDER = (0, 0, 0)

HD_WIDTH = 760
HD_HEIGHT = 1000
MINI_WIDTH = int(HD_WIDTH / 2)
MINI_HEIGHT = int(HD_HEIGHT / 2)

logger = logging.getLogger()


def setup_logger():
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)


def crop_center(image, target_width, target_height):
    """
    crop at the center
    return a new Image instance
    """
    width, height = image.size
    if width == target_width:
        delta = (height - target_height) / 2
        box = (0, delta, width, height - delta)
    else:
        delta = (width - target_width) / 2
        box = (delta, 0, width - delta, height)

    return image.crop(box)


def add_frame(image):
    """Adds the polaroid frame around the image"""
    frame = Image.new(
        "RGB",
        (
            BORDER_SIZE + IMAGE_LEFT + HD_WIDTH + IMAGE_RIGHT + BORDER_SIZE,
            BORDER_SIZE + IMAGE_TOP + HD_HEIGHT + IMAGE_BOTTOM + BORDER_SIZE,
        ),
        COLOR_BORDER,
    )

    # Create outer and inner borders
    draw = ImageDraw.Draw(frame)
    draw.rectangle(
        (
            BORDER_SIZE,
            BORDER_SIZE,
            frame.size[0] - BORDER_SIZE * 2,
            frame.size[1] - BORDER_SIZE * 2,
        ),
        fill=COLOR_FRAME,
    )

    # Add the source image
    frame.paste(image, (IMAGE_LEFT, IMAGE_TOP))

    return frame


def build_target(filepath, folder):
    """
    return a new folder path
    """
    name, _ = path.splitext(path.basename(filepath))
    return path.join(path.dirname(path.realpath(__file__)), folder, name + ".jpg")


def can_create_mini_polaroid(image):
    width, height = image.size
    return width >= MINI_WIDTH and height > MINI_HEIGHT


def can_create_hd_polaroid(image):
    width, height = image.size
    return width >= HD_WIDTH and height > HD_HEIGHT


def rescale_keep_one_side(image, keep_width, keep_height):
    """
    rescale but force one side.
    if in landscape -> keep height
    if in portrait  -> keep width
    """
    width, height = image.size

    if width > height:
        resized_height = keep_height
        resized_width = int(round((keep_height / float(height)) * width))
    else:
        resized_width = keep_width
        resized_height = int(round((keep_width / float(width)) * height))

    return image.resize(
        (resized_width, resized_height), resample=Image.LANCZOS, reducing_gap=3
    )


def create_hd_polaroid(image):
    scaled_image = rescale_keep_one_side(image, HD_WIDTH, HD_HEIGHT)
    croped_image = crop_center(scaled_image, HD_WIDTH, HD_HEIGHT)
    frammed_image = add_frame(croped_image)
    logger.info("  image size is %s", image.size)
    logger.info(" scaled size is %s", scaled_image.size)
    logger.info("cropped size is %s", croped_image.size)
    return frammed_image


def save_to(image, original_filepath, folder):
    target_hd = build_target(original_filepath, folder)
    image.save(target_hd)
    return target_hd


def main(args):
    """
    main
    """
    filepath = args[0]
    source_image = Image.open(filepath)

    if can_create_hd_polaroid(source_image):
        hd_image = create_hd_polaroid(source_image)
        hd_path = save_to(hd_image, filepath, "polaroid-hd")
        logger.info("saved HD to %s", hd_path)
    else:
        logger.warning(
            "%s : %s is too small to have a polaroid of : %s X %s",
            filepath,
            source_image.size,
            HD_WIDTH,
            HD_HEIGHT,
        )

    if can_create_mini_polaroid(source_image):
        mini_image = rescale_keep_one_side(source_image, MINI_WIDTH, MINI_HEIGHT)
        mini_path = save_to(mini_image, filepath, "polaroid-mini")
        logger.info("saved mini to %s", mini_path)
    else:
        logger.warning(
            "%s : %s is too small to have a polaroid of : %s X %s",
            filepath,
            source_image.size,
            MINI_WIDTH,
            MINI_HEIGHT,
        )


if __name__ == "__main__":
    setup_logger()
    main(sys.argv[1:])
