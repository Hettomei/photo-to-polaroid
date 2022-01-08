"""
convert to polaroid
Thanks to https://raw.githubusercontent.com/thegaragelab/pythonutils/master/polaroid/polaroid.py
"""

import argparse
import sys
import logging
from os import path
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile

from PIL import Image, ImageDraw

BORDER_SIZE = 1
BORDER_COLOR = (100, 100, 100)
COLOR_FRAME = (255, 255, 255)

MEASURES = {
    "medium-lightframe": SimpleNamespace(
        width=760,
        height=1000,
        frame=SimpleNamespace(top=100, bottom=200, left=70, right=70),
    ),
    "medium": SimpleNamespace(
        width=760,
        height=1000,
        frame=SimpleNamespace(top=140, bottom=280, left=70, right=70),
    ),
    "mini": SimpleNamespace(
        width=380,
        height=500,
        frame=SimpleNamespace(top=70, bottom=140, left=35, right=35),
    ),
}

logger = logging.getLogger()


def setup_logger():
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)


def parse(sys_args):
    parser = argparse.ArgumentParser(description="Convert photos into polaroid.")
    parser.add_argument(
        "--file",
        dest="filepath",
        action="store",
        help="File path to convert",
    )

    parser.add_argument(
        "--from",
        dest="folder",
        action="store",
        help="Folder path to convert all jpg jpeg and png",
    )

    parser.add_argument(
        "--size",
        dest="size",
        choices=sorted(MEASURES.keys()),
        action="store",
        help="the size of the polaroid",
        default="medium",
    )

    parser.add_argument(
        "--to",
        dest="to_folder",
        action="store",
        help=(
            "The destination folder. "
            "passing a/b/c will create ./a/b/c if it does not exist. "
            "By default create a temp folder"
        ),
    )

    return parser.parse_args(sys_args)


def prepare_env(options):
    options.files = set()

    if options.filepath:
        options.files.add(Path(options.filepath).resolve())

    if options.folder:
        options.files.update(
            (
                p.resolve()
                for p in Path(options.folder).glob("*")
                if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
            )
        )

    if options.to_folder:
        os.makedirs(options.to_folder)
    else:
        options.to_folder = tempfile.mkdtemp(prefix=f"to-polaroid-{options.size}-")

    options.measures = MEASURES[options.size]

    return options


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
    return path.join(folder, name + ".jpg")


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
    logger.debug("use %s", measures)
    logger.debug("  image size is %s", image.size)
    logger.debug(" scaled size is %s", scaled_image.size)
    logger.debug("cropped size is %s", croped_image.size)
    return frammed_image


def save_to(image, original_filepath, folder):
    target = build_target(original_filepath, folder)
    image.save(target)
    logger.info("saved to %s", target)
    return target


def convert_picture(filepath, options):
    source_image = Image.open(filepath)
    measures = options.measures

    if can_create_polaroid(source_image, measures):
        hd_image = create_polaroid(source_image, measures)
        save_to(hd_image, filepath, options.to_folder)
    else:
        logger.warning(
            "%s : %s is too small to have a polaroid of : %s",
            filepath,
            source_image.size,
            (measures.width, measures.height),
        )


def main(args):
    options = parse(args)
    options = prepare_env(options)

    for filepath in options.files:
        logger.info("Try to convert %s", filepath)
        convert_picture(filepath, options)


if __name__ == "__main__":
    setup_logger()
    main(sys.argv[1:])
