"""
app.py

Main app function file for running the program, delegating the tagging operations to different threads.
"""

import logging
import os

from google.cloud import vision
from rich.progress import Progress, BarColumn
from rich.traceback import install

from . import INPUT_PATH, TEMP_PATH
from .helpers import valid_extension, get_extension, convert_to_bytes
from .process import MasterFileProcessor

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
install()

def run():
    client = vision.ImageAnnotatorClient()

    # Locate valid files
    files = os.listdir(INPUT_PATH)
    select = list(filter(lambda file: valid_extension(get_extension(file)), files))

    if len(select) == 0:
        logger.fatal("No valid files located.")
        return
    else:
        logger.info(f"Found {len(select)} valid files")

    # Create the 'temp' directory
    if not os.path.exists(TEMP_PATH):
        logger.info("Creating temporary processing directory")
        os.makedirs(TEMP_PATH)

    try:
        with Progress(
                "[progress.description]{task.description}",
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.0f}%",
        ) as progress:
            mp = MasterFileProcessor(select, 3, convert_to_bytes("1280 KB"), True, client=client, progress=progress)
            logger.info('MasterFileProcessor created.')
            mp.load()
            logger.info('Finished loading/starting initial threads.')
            mp.join()
            logger.info('Finished joining threads, now quitting.')

    except Exception as error:
        logger.error(str(error))
        raise
    finally:
        os.rmdir(TEMP_PATH)
        logger.info("Temporary directory removed.")
