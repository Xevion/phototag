import io
import sys
import os
import time
import rawpy
import imageio
import progressbar
import shutil
import logging

from threading import Thread
from google.cloud import vision
from package import xmp
from PIL import Image

from .xmp import XMPParser
from .process import FileProcessor
from . import INPUT_PATH, TEMP_PATH, OUTPUT_PATH
from . import RAW_EXTS, LOSSY_EXTS

log = logging.getLogger("app")


def run():
    client = vision.ImageAnnotatorClient()

    # Find files we want to process based on if they have a corresponding .XMP
    log.info("Locating processable files...")
    files = os.listdir(INPUT_PATH)
    select = [
        file
        for file in files
        if os.path.splitext(file)[1][1:].lower() in (RAW_EXTS + LOSSY_EXTS)
    ]
    log.info(f"Found {len(select)} valid files")
    if len(select) <= 0:
        log.fatal("No valid files found, exiting early")
        return

    # Create the 'temp' directory
    if not os.path.exists(TEMP_PATH):
        log.info("Creating temporary processing directory")
        os.makedirs(TEMP_PATH)

    try:
        # Process files via Threading
        processors = [FileProcessor(file) for file in select]
        threads = [Thread(target=process.run, args=(client,)) for process in processors]
        # Start
        for i, thread in enumerate(threads):
            log.info(f"Processing file '{processors[i].file_name}'...")
            thread.start()
        # Wait
        for thread in threads:
            thread.join()
        # for process in progressbar.progressbar(processors, redirect_stdout=True, term_width=110):

    except Exception as error:
        log.error(str(error))
        log.warning("Removing temporary directory before raising exception.")
        os.rmdir(TEMP_PATH)
        raise

    # Remove the directory, we are done here
    log.info("Removing temporary directory.")
    os.rmdir(TEMP_PATH)
