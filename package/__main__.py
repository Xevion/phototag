import os
import logging

from . import INPUT_PATH, OUTPUT_PATH

# Ensure that 'input' and 'output' directories are created
if not os.path.exists(INPUT_PATH):
    logging.fatal('Input directory did not exist, creating and quitting.')
    os.makedirs(INPUT_PATH)

if not os.path.exists(OUTPUT_PATH):
    logging.info('Output directory did not exist. Creating...')
    os.makedirs(OUTPUT_PATH)