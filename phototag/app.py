"""
app.py

Main app function file for running the program, delegating the tagging operations to different threads.
"""

import logging
import os
from threading import Thread

from google.cloud import vision

from . import INPUT_PATH, TEMP_PATH
from .helpers import valid_extension, get_extension
from .process import FileProcessor

log = logging.getLogger("app")


def run():
    client = vision.ImageAnnotatorClient()

    # Locate valid files
    files = os.listdir(INPUT_PATH)
    select = list(filter(lambda file: valid_extension(get_extension(file)), files))

    if len(select) == 0:
        log.fatal("No valid files located.")
        return
    else:
        log.info(f"Found {len(select)} valid files")

    # Create the 'temp' directory
    if not os.path.exists(TEMP_PATH):
        log.info("Creating temporary processing directory")
        os.makedirs(TEMP_PATH)

    try:
        # Process files with threading
        processors = [FileProcessor(file) for file in select]
        threads = [Thread(target=process.run, args=(client,)) for process in processors]

        # Start threads for each file
        for i, thread in enumerate(threads):
            log.info(f"Processing file '{processors[i].file_name}'...")
            thread.start()

        # Wait for each thread to complete before stopping
        for thread in threads:
            thread.join()

    except Exception as error:
        log.error(str(error))
        raise
    finally:
        os.rmdir(TEMP_PATH)
        log.info("Temporary directory removed.")
