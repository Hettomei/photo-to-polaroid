"""
convert to polaroid
Thanks to https://raw.githubusercontent.com/thegaragelab/pythonutils/master/polaroid/polaroid.py
"""

import sys
from os import path
from PIL import Image, ImageDraw

# Image size constraints
IMAGE_SIZE = 800
IMAGE_TOP = 50
IMAGE_BOTTOM = 150
IMAGE_LEFT = 50
IMAGE_RIGHT = 50

BORDER_SIZE = 3

COLOR_FRAME = (255, 255, 255)
COLOR_BORDER = (0, 0, 0)


def scale_image(image, width, height):
    """scale down"""
    if image.size[0] > width:
        return image.resize((width, height), Image.ANTIALIAS)

    return image.resize((width, height), Image.BICUBIC)


def crop_image(image):
    """
    return a new Image instance
    """
    if image.size[0] > image.size[1]:
        delta = (image.size[0] - image.size[1]) / 2
        box = (delta, 0, image.size[0] - delta, image.size[1])
    elif image.size[1] > image.size[0]:
        delta = (image.size[1] - image.size[0]) / 2
        box = (0, delta, image.size[0], image.size[1] - delta)

    image = image.crop(box)
    image.load()
    return image


def add_frame(image):
    """Adds the frame around the image"""
    # Create the frame
    frame = Image.new(
        "RGB",
        (IMAGE_SIZE + IMAGE_LEFT + IMAGE_RIGHT, IMAGE_SIZE + IMAGE_TOP + IMAGE_BOTTOM),
        COLOR_BORDER,
    )

    # Create outer and inner borders
    draw = ImageDraw.Draw(frame)
    draw.rectangle(
        (
            BORDER_SIZE,
            BORDER_SIZE,
            frame.size[0] - BORDER_SIZE,
            frame.size[1] - BORDER_SIZE,
        ),
        fill=COLOR_FRAME,
    )
    draw.rectangle(
        (
            IMAGE_LEFT - BORDER_SIZE,
            IMAGE_TOP - BORDER_SIZE,
            IMAGE_LEFT + IMAGE_SIZE + BORDER_SIZE,
            IMAGE_TOP + IMAGE_SIZE + BORDER_SIZE,
        ),
        fill=COLOR_BORDER,
    )
    # Add the source image
    frame.paste(image, (IMAGE_LEFT, IMAGE_TOP))
    # All done
    return frame


def build_target(filepath, folder):
    """
    return a new folder
    """
    name, _ = path.splitext(path.basename(filepath))
    return path.join(path.dirname(path.realpath(__file__)), folder, name + ".jpg")


def main(args):
    """
    main
    """
    filepath = args[0]
    source_image = Image.open(filepath)
    source_image.load()

    source_image = scale_image(crop_image(source_image), IMAGE_SIZE, IMAGE_SIZE)
    source_image_hd = add_frame(source_image)

    target_hd = build_target(filepath, "polaroid-hd")
    source_image_hd.save(target_hd)
    print("saved to", target_hd)

    source_image_mini = scale_image(source_image_hd, 300, 333)
    target_mini = build_target(filepath, "polaroid-mini")
    source_image_mini.save(target_mini)
    print("saved to", target_mini)


if __name__ == "__main__":
    main(sys.argv[1:])
