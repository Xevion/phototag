"""
helpers.py

Simple helper functions and constants separated from the primary application functionality.
"""
import logging
import os
import random
import re
import string
from glob import glob
from pathlib import Path
from typing import List, Optional, Tuple, Generator

from phototag import CWD
from phototag.constants import LOSSY_EXTS, RAW_EXTS
from phototag.exceptions import PhototagException, InvalidSelectionError

ALL_EXTENSIONS = RAW_EXTS + LOSSY_EXTS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

byte_magnitudes = {
    "B": 1,
}

# Generate every variation of byte suffixes
for magnitude, suffix_kibi in enumerate(["K", "M", "G", "T", "P", "E", "Z", "Y"], start=1):
    suffix_kilo = suffix_kibi.lower()
    values: List[Tuple[str, int]] = [
        # Kibi (1024)
        (f"{suffix_kibi}B", 1024 ** magnitude),
        (f"{suffix_kibi}b", 1024 ** magnitude // 8),
        (f"{suffix_kibi}iB", 1024 ** magnitude),
        (f"{suffix_kibi}ib", 1024 ** magnitude // 8),
        # Kilo (1000)
        (f"{suffix_kilo}B", 1000 ** magnitude),
        (f"{suffix_kilo}b", 1000 ** magnitude // 8),
        (f"{suffix_kilo}iB", 1000 ** magnitude),
        (f"{suffix_kilo}ib", 1000 ** magnitude // 8)
    ]

    for suffix, scale in values:
        byte_magnitudes[suffix] = scale


def valid_extension(extension: str) -> bool:
    """
    :param extension: The extension you wish to test. Prepended dots are acceptable.
    :return: A boolean describing the validity of the extension in the context of the Phototag application.
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
    :param length: An integer describing the intended length of the generated string.
    :return: A random series of characters *length* characters long.
    """
    return ''.join(random.choices(string.ascii_letters, k=length))


def get_temp_directory(directory: str, start: str = "temp", append_random: int = 0) -> str:
    """
    :param directory: A valid directory where the temporary directory is intended to be created.
    :param start: The string the directory should start with.
    :param append_random: Whether to always include a random series of characters.
    :return: A valid path to a directory that has not yet been created.
    """
    temp: str = ""

    # Generate directory names until one matches (usually first or second try)
    while os.path.exists(temp):
        temp = os.path.join(directory, (start + "_" + random_characters(append_random)) if append_random > 0 else start)
        if append_random >= 128:
            raise PhototagException(
                "Could not find a valid temporary directory name. Please try again in a different directory."
            )
        append_random += (3 if append_random == 0 else 1)
    return temp


def convert_to_bytes(size_string: str) -> int:
    """
    Converts the string representation of data into it's integer byte equivalent.

    :param size_string: A string representation of data size, a integer followed by 1-2 letters indicating unit.
    :return: The number of bytes the given string is equivalent to.
    """
    match = re.match(r"\s*(\d+)\s*(\wi?[Bb])\s*", size_string)
    return int(match.group(1)) * byte_magnitudes.get(match.group(2), 0)


def walk(root: Path, current: Optional[Path] = None, depth: Optional[int] = None) -> Generator[
    Path, None, None]:
    """
    Recursively walk through a directory and yield all files found.
    """
    root_abs_depth: int = len(root.parents)

    if depth is not None and depth < 0:
        depth = None

    for item in (current or root).iterdir():
        if item.is_file():
            yield item.resolve()
        if not item.is_dir():
            continue

        # Recursive handling
        cur_depth: int = len(item.resolve().parents) - root_abs_depth - 1
        if depth is None or cur_depth < depth:
            yield from walk(root, current=item, depth=depth)


def path_to_match_mode(path: Path, match_mode: str, root: Optional[Path] = None) -> str:
    """
    Converts a path to a string based on the match mode.
    :param path: The path to convert
    :param match_mode: The match mode to use
    :param root: The relative directory to use for 'relative' match mode. Defaults to the current working directory.
    """
    root = root or Path.cwd()
    if match_mode == "relative":
        return str(path.relative_to(root or Path.cwd()))
    elif match_mode == "absolute":
        return str(path.resolve())
    elif match_mode == "filename":
        return path.name
    else:
        raise ValueError(f"Invalid match mode: {match_mode}")


def select_files(files: List[str], regex: Optional[str], glob_pattern: Optional[str]) -> List[str]:
    """
    Helper function for selecting files in the CWD (or subdirectories, via Glob) and filtering them.
    Combines direct file argument selections, RegEx filters and Glob patterns together.

    :param files: Specific files chosen by the user.
    :param regex: A full RegEx matching pattern
    :param glob_pattern: A Glob pattern
    :return: A list of files relative to the CWD
    """
    # Just add all files in current working directory
    if all:
        files.extend(os.listdir(CWD))
    else:
        # RegEx option pattern matching
        if regex:
            files.extend(
                filter(lambda filename: re.match(re.compile(regex), filename) is not None, os.listdir(CWD))
            )

        # Glob option pattern matching
        if glob_pattern:
            files.extend(glob(glob_pattern))

    # Format file selection into relative paths, filter down to 'valid' image files
    files = list(dict.fromkeys(os.path.relpath(file) for file in files))
    select = list(filter(lambda filename: valid_extension(get_extension(filename)), files))

    if len(select) == 0:
        logger.debug(f'{len(files)} files found, 0 images found.')
        if len(files) == 0:
            raise InvalidSelectionError('No files selected.')
        else:
            raise InvalidSelectionError('No valid images selected.')
    else:
        logger.info(f'Found {len(select)} valid images out of {len(files)} files selected.')

    return files
