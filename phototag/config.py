import os
import sys
import configparser

SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_ROOT, "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.ini")
config = configparser.ConfigParser()


def quicksave():
    with open(CONFIG_PATH, "w+") as file:
        config.write(file)


if not os.path.exists(CONFIG_PATH):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    config["google"] = {"credentials": ""}
    quicksave()
else:
    with open(CONFIG_PATH, "r") as file:
        config.read_file(file)
