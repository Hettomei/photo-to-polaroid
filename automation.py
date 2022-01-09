"""
Help people on windows
"""
import logging
import sys
from os import path
import shutil

import polaroid

logger = logging.getLogger("polaroid")


def setup_logger():
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)


def try_delete(folder_path):
    try:
        shutil.rmtree(folder_path)
    except FileNotFoundError:
        logger.info("%s not present", folder_path)


def main():
    current_folder = path.dirname(__file__)

    source_pics_path = path.join(current_folder, "A polaroidiser")
    croped_pics_path = path.join(current_folder, "polaroid-decoupe")
    full_pics_path = path.join(current_folder, "polaroid-entiere")

    try_delete(croped_pics_path)
    try_delete(full_pics_path)

    polaroid.main(
        [
            "--from",
            source_pics_path,
            "--to",
            croped_pics_path,
            "--final-width",
            "500",
        ]
    )
    polaroid.main(
        [
            "--from",
            source_pics_path,
            "--to",
            full_pics_path,
            "--final-width",
            "500",
            "--no-crop",
        ]
    )


if __name__ == "__main__":
    setup_logger()
    main()
