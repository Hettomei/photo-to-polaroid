"""
convert to polaroid
Thanks to https://raw.githubusercontent.com/thegaragelab/pythonutils/master/polaroid/polaroid.py
"""

import sys
import logging
from os import path
from types import SimpleNamespace

from PIL import Image, ImageDraw

BORDER_SIZE = 1
BORDER_COLOR = (100, 100, 100)
COLOR_FRAME = (255, 255, 255)

logger = logging.getLogger()


def setup_logger():
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)


def crop_center(image, measures):
    """
    crop at the center
    return a new Image instance
    """
    width, height = image.size
    if width == measures.width:
        delta = (height - measures.height) / 2
        box = (0, delta, width, height - delta)
    else:
        delta = (width - measures.width) / 2
        box = (delta, 0, width - delta, height)

    return image.crop(box)


def add_frame(image, measures):
    """Adds the polaroid frame around the image"""
    frame = Image.new(
        "RGB",
        (
            BORDER_SIZE
            + measures.frame.left
            + measures.width
            + measures.frame.right
            + BORDER_SIZE,
            BORDER_SIZE
            + measures.frame.top
            + measures.height
            + measures.frame.bottom
            + BORDER_SIZE,
        ),
        BORDER_COLOR,
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
    frame.paste(image, (measures.frame.left, measures.frame.top))

    return frame


def build_target(filepath, folder):
    """
    return a new folder path
    """
    name, _ = path.splitext(path.basename(filepath))
    return path.join(path.dirname(path.realpath(__file__)), folder, name + ".jpg")


def can_create_polaroid(image, measures):
    width, height = image.size
    return width >= measures.width and height > measures.height


def rescale_keep_one_side(image, measures):
    """
    rescale but force one side.
    if in landscape -> keep height
    if in portrait  -> keep width
    """
    width, height = image.size

    if width > height:
        resized_height = measures.height
        resized_width = int(round((measures.height / float(height)) * width))
    else:
        resized_width = measures.width
        resized_height = int(round((measures.width / float(width)) * height))

    return image.resize(
        (resized_width, resized_height), resample=Image.LANCZOS, reducing_gap=3
    )


def create_polaroid(image, measures):
    scaled_image = rescale_keep_one_side(image, measures)
    croped_image = crop_center(scaled_image, measures)
    frammed_image = add_frame(croped_image, measures)
    logger.info("use %s", measures)
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

    # other proportion
    # hd_measures = SimpleNamespace(
    #     width=760,
    #     height=1000,
    #     # frame=SimpleNamespace(top=100, bottom=200, left=70, right=70),
    # )
    hd_measures = SimpleNamespace(
        width=760,
        height=1000,
        frame=SimpleNamespace(top=140, bottom=280, left=70, right=70),
    )
    mini_measures = SimpleNamespace(
        width=380,
        height=500,
        frame=SimpleNamespace(top=70, bottom=140, left=35, right=35),
    )
    if can_create_polaroid(source_image, hd_measures):
        hd_image = create_polaroid(source_image, hd_measures)
        hd_path = save_to(hd_image, filepath, "polaroid-hd")
        logger.info("saved HD to %s", hd_path)
    else:
        logger.warning(
            "%s : %s is too small to have a polaroid of : %s",
            filepath,
            source_image.size,
            hd_measures,
        )

    if can_create_polaroid(source_image, mini_measures):
        mini_image = create_polaroid(source_image, mini_measures)
        mini_path = save_to(mini_image, filepath, "polaroid-mini")
        logger.info("saved mini to %s", mini_path)
    else:
        logger.warning(
            "%s : %s is too small to have a polaroid of : %s",
            filepath,
            source_image.size,
            mini_measures,
        )


if __name__ == "__main__":
    setup_logger()
    main(sys.argv[1:])
