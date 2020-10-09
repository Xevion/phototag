"""
config.py

Assist with creating, accessing and saving to a configuration file located in the script installation folder.
"""

import configparser
import os

SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))  # Script installation folder
CONFIG_DIR = os.path.join(SCRIPT_ROOT, "config")  # Configuration file folder
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.ini")  # Configuration file
config = configparser.ConfigParser()


def quicksave():
    """Simple function for saving current configuration state to file"""
    with open(CONFIG_PATH, "w+") as file:
        config.write(file)


# If file does not exist
if not os.path.exists(CONFIG_PATH):
    # If folder does not exist
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    # Default configuration data
    config["google"] = {"credentials": ""}
    config["limits"] = {
        "image_count": 16,  # 16 images in memory at any time
        "buffer_size": "256 MB",  # 256 MB of images in memory at any time,
        "single_override": True  # disregard previous filters to keep at least 1 image in rotation
    }

    quicksave()
else:
    # File exists, so just read
    with open(CONFIG_PATH, "r") as file:
        config.read_file(file)
