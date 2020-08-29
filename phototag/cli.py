"""
cli.py

The file responsible for providing commandline functionality to the user.
"""

import logging
import os
import re
import shutil
from typing import Tuple
from glob import glob

import click

from . import config, INPUT_PATH
from .helpers import get_extension, valid_extension

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@click.group()
def cli():
    """Base CLI command group"""
    pass


@cli.command('run', short_help='Run the tagging service.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('-a', '--all', is_flag=True, help='Add all files in the current directory to be tagged.')
@click.option('-r', '--regex', help='Use RegEx to match files in the current directory')
@click.option('-g', '--glob', 'glob_pattern', help='Use Glob (UNIX-style file pattern matching) to match files.')
def run(files: Tuple[str], all: bool = False, regex: str = None, glob_pattern: str = None):
    """
    Run tagging on FILES.

    Files can also be selected using --all, --regex and --glob.

    """
    files = list(files)

    # Just add all files in current working directory
    if all:
        files.extend(os.listdir(INPUT_PATH))
    else:
        # RegEx option pattern matching
        if regex:
            files.extend(
                filter(lambda filename: re.match(re.compile(regex), filename) is not None, os.listdir(INPUT_PATH))
            )

        # Glob option pattern matching
        if glob_pattern:
            files.extend(glob(glob_pattern))

    files = list(dict.fromkeys(os.path.relpath(file) for file in files))
    select = list(filter(lambda filename: valid_extension(get_extension(filename)), files))
    if len(select) == 0:
        if len(files) == 0:
            logger.info('No files selected.')
        else:
            logger.info('No valid images selected.')
    else:
        logger.debug(f'{len(select)} valid images out of {len(files)} files selected.')

    print(files)
    # from .app import run
    #
    # run()


@cli.command('auth')
@click.argument("path", type=click.Path(exists=True))
@click.option("-m", "--move", default=False, show_default=True, prompt=True,
              help="Move instead of copying the credentials file", )
def auth(path, move):
    """
    A utility command for copying the Downloaded Google Vision API Credentials file to the configuration folder.
    """

    # Make sure relative path references are made absolute
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    # Verify that the file exists
    if not os.path.isfile(path):
        if os.path.isdir(path):
            logger.warning("The specified path is a directory, not a file.")
        else:
            logger.warning("The specified path does not exist.")
    else:
        # Identify the final location of the file in the config directory
        _, head = os.path.split(path)
        new_path = os.path.join(config.SCRIPT_ROOT, "config", head)

        # Move or copy the file
        if move:
            shutil.move(path, new_path)
            logger.info("Successfully moved file to configuration file...")
        elif not move:
            shutil.copy(path, new_path)
            logger.info("Successfully copied file to configuration folder...")

        # Update the configuration file to point to the
        config.config["google"]["credentials"] = head
        config.quicksave()

        logger.info(f"Configuration updated.")
