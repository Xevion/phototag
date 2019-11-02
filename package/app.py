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
    files = os.listdir(INPUT_PATH)
    select = [file for file in files if os.path.splitext(file)[1] != '.xmp']

    # Create the 'temp' directory
    print(f'Initializing file processing for {len(select)} files...')
    os.makedirs(TEMP_PATH)

    try:
        # Process files
        for index, file in progressbar.progressbar(list(enumerate(select)), redirect_stdout=True, term_width=110):
            name, ext = os.path.splitext(file)
            ext = ext.lower().strip('.')
            # Raw files contain their metadata in an XMP file usually
            if ext in RAW_EXTS:
                print('Processing file {}, \'{}\''.format(index + 1, xmps[0]), end=' | ')
                file = FileProcessor(file, xmps[0])
                file.run(client)
            elif ext in LOSSY_EXTS:
                print('Processing file {}, \'{}\''.format(index + 1, file), end=' | ')
                file = FileProcessor(file)
                file.run(client)
    except:
        os.rmdir(TEMP_PATH)
        raise

    # Remove the directory, we are done here
    print('Cleaning up temporary directory...')
    os.rmdir(TEMP_PATH)