"""
helpers.py

Simple helper functions and constants separated from the primary application functionality.
"""
import os
import random
import re
import string

from phototag import LOSSY_EXTS, RAW_EXTS

ALL_EXTENSIONS = RAW_EXTS + LOSSY_EXTS

byte_magnitudes = {
    "B": 1024 ** 0,
    "KB": 1024 ** 1,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3,
    "TB": 1024 ** 4
}


def valid_extension(extension: str) -> bool:
    """
    :param extension: The extension you wish to test. Prepended dots are acceptable.
    :return: A boolean describing the validity of the extension in the context of the phototag application.
    """
    return extension.lstrip('.') in ALL_EXTENSIONS


def get_extension(filename: str) -> str:
    """
    :param filename: A filename or path with a file in it. Relative and absolute paths accepted. Must have an extension.
    :return: The extension with the prepended dot removed and the extension in lowercase
    """
    return os.path.splitext(filename)[1][1:].lower()


def random_characters(length: int) -> str:
    """
    :param length: A integer describing the intended length of the generated string.
    :return: A random series of characters *length* characters long.
    """
    return ''.join(random.choices(string.ascii_letters, k=length))


def get_temp_directory(directory: str, start: str = "temp", append_random: int = 0) -> str:
    """
    :param directory: A valid directory where the temporary directory is intended to be created.
    :param start: The string the directory should start with.
    :param append_random: Whether or not to always include a random series of characters.
    :return: A valid path to a directory that has not yet been created.
    """
    temp: str = ""

    # Generate directory names until one matches (usually first or second try)
    while os.path.exists(temp):
        temp = os.path.join(directory, (start + "_" + random_characters(append_random)) if append_random > 0 else start)
        if append_random >= 128:
            raise Exception(
                "Could not find a valid temporary directory name. Please try again in a different directory."
            )
        append_random += (3 if append_random == 0 else 1)
    return temp


def convert_to_bytes(display_size: str) -> int:
    """
    Converts the string representation of data into it's integer byte equivalent.

    :param display_size: A string representation of data size, a integer followed by 1-2 letters indicating unit.
    :return: The number of bytes the given string is equivalent to.
    """
    match = re.match(r"(\d+) (\w{1,2})", display_size)
    return int(match.group(1)) * byte_magnitudes[match.group(2)]
