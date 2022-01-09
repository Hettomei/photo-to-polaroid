"""
convert to polaroid
"""

import argparse
import sys
import logging
from os import path
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile

from PIL import Image, ImageDraw, ImageOps

BORDER_SIZE = 1
BORDER_COLOR = (100, 100, 100)
COLOR_FRAME = (255, 255, 255)

MEASURE = SimpleNamespace(
    width=380,
    height=500,
    frame=SimpleNamespace(top=70, bottom=140, left=35, right=35),
)

# ratio  =  width / heigth
# width  = heigth * ratio
# heigth =  width / ratio
RATIO = MEASURE.width / MEASURE.height  # ratio of the inner picture of a polaroid
RATIO_LEFT_FRAME = MEASURE.width / MEASURE.frame.left
RATIO_RIGHT_FRAME = MEASURE.width / MEASURE.frame.right
RATIO_TOP_FRAME = MEASURE.width / MEASURE.frame.top
RATIO_BOTTOM_FRAME = MEASURE.width / MEASURE.frame.bottom

logger = logging.getLogger("polaroid")


def setup_logger():
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")

    console = logging.StreamHandler(sys.stdout)
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
        "--final-width",
        dest="final_width",
        action="store",
        help=(
            "The width of the inner polaroid in pixel. "
            "Other values are computed. If no values : do not resize it."
        ),
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

    parser.add_argument(
        "--no-crop",
        dest="no_crop",
        action="store_true",
        help="never cut the picture before adding a polaroid frame",
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
        options.to_folder = tempfile.mkdtemp(prefix="to-polaroid-")

    if options.final_width:
        options.final_width = int(options.final_width)

    return options


def crop_center(image):
    """
    crop at the center
    return a new Image instance
    """
    if image.width > image.height:
        new_width = round(RATIO * image.height)
        new_height = image.height
    else:
        new_height = round(image.width / RATIO)
        new_width = image.width

    return ImageOps.fit(image, (new_width, new_height))


def pad_center(image):
    """
    pad at the center
    return a new Image instance
    """
    if image.width > image.height:
        new_width = round(RATIO * image.height)
        new_height = image.height
    else:
        new_height = round(image.width / RATIO)
        new_width = image.width

    return ImageOps.pad(image, (new_width, new_height))


def add_frame(image):
    """Adds the polaroid frame around the image"""
    left_frame_size = round(image.width / RATIO_LEFT_FRAME)
    top_frame_size = round(image.width / RATIO_TOP_FRAME)

    frame = Image.new(
        "RGB",
        (
            BORDER_SIZE
            + left_frame_size
            + image.width
            + round(image.width / RATIO_RIGHT_FRAME)
            + BORDER_SIZE,
            BORDER_SIZE
            + top_frame_size
            + image.height
            + round(image.width / RATIO_BOTTOM_FRAME)
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
            frame.width - BORDER_SIZE * 2,
            frame.height - BORDER_SIZE * 2,
        ),
        fill=COLOR_FRAME,
    )

    # Add the source image
    frame.paste(image, (left_frame_size, top_frame_size))

    return frame


def save_to(image, filepath, folder, more=""):
    name, _ = path.splitext(path.basename(filepath))
    target = path.join(folder, name + more + ".jpg")
    image.save(target)
    return target


def create_polaroid(filepath, options):
    source_image = Image.open(filepath)
    log_size("  image size is %s, ratio is %s", source_image)

    if options.no_crop:
        croped_image = pad_center(source_image)
    else:
        croped_image = crop_center(source_image)
    log_size(" croped size is %s, ratio is %s", croped_image)

    if options.final_width:
        resized_image = croped_image.resize(
            (options.final_width, round(options.final_width / RATIO)),
            resample=Image.LANCZOS,
            reducing_gap=3,
        )
        log_size("  thumb size is %s, ratio is %s", resized_image)
    else:
        resized_image = croped_image

    frammed_image = add_frame(resized_image)
    log_size("frammed size is %s, ratio is %s", frammed_image)

    savepath = save_to(frammed_image, filepath, options.to_folder)

    logger.info("%s saved to %s", filepath, savepath)


def log_size(txt, image):
    logger.debug(txt, image.size, image.width / image.height)


def main(args):
    options = parse(args)
    options = prepare_env(options)
    logger.debug(options)

    for filepath in options.files:
        create_polaroid(filepath, options)


if __name__ == "__main__":
    setup_logger()
    main(sys.argv[1:])
