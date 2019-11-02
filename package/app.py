import io
import sys
import os
import time
import rawpy
import imageio
import progressbar
import shutil
import logging

from google.cloud import vision

from .xmp import XMPParser
from .process import FileProcessor
from . import INPUT_PATH, TEMP_PATH, OUTPUT_PATH, PROCESSING_PATH
from . import RAW_EXTS, LOSSY_EXTS

# Process a single file in these steps:
# 1) Create a temporary file
# 2) Send it to GoogleAPI
# 3) Read XMP, then write new tags to it
# 4) Delete temporary file, move NEF/JPEG and XMP

# Driver code for the package
def run():
    # Client
    client = vision.ImageAnnotatorClient()

    # Find files we want to process based on if they have a corresponding .XMP
    logging.info('Locating processable files...')
    files = os.listdir(INPUT_PATH)
    select = [file for file in files if os.path.splitext(file)[1] != '.xmp']

    # Create the 'temp' directory
    logging.info(f'Found {len(files)} valid files, beginning processing...')
    os.makedirs(TEMP_PATH)

    try:
        # Process files
        for index, file in progressbar.progressbar(list(enumerate(select)), redirect_stdout=True, term_width=110):
            _, ext = os.path.splitext(file)
            if ext in LOSSY_EXTS or ext in RAW_EXTS:
                logging.info(f"Processing file '{file}'...")
                file = FileProcessor(file)
                file.run(client)
    except:
        logging.warning('Removing temporary directory before raising exception.')
        os.rmdir(TEMP_PATH)
        raise

    # Remove the directory, we are done here
    logging.info('Removing temporary directory.')
    os.rmdir(TEMP_PATH)