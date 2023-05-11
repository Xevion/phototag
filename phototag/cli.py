"""
cli.py

The file responsible for providing commandline functionality to the user.
"""

import logging
import os
import shutil
from typing import Tuple

import click
from google.cloud import vision
from rich.progress import Progress, BarColumn

from phototag import config, TEMP_PATH
from phototag.exceptions import InvalidSelectionError
from phototag.helpers import select_files, convert_to_bytes
from phototag.process import MasterFileProcessor

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
@click.option('--max-threads', type=int, help='The maximum number of threads that can be running at any point')
@click.option('--max-buffer-size', 'max_buffer',
              help='Keep the total size of the files in memory at or below this point')
@click.option('--forget', is_flag=True, help='Don\'t utilize labels received from the Vision API previously.')
@click.option('--overwrite', is_flag=True, help='Instead of adding tags, clear and overwrite them')
@click.option('-d', '--dry-run', is_flag=True, help='Dry-run mode: Don\'t actually write to or modify files.')
@click.option('-t', '--test', is_flag=True,
              help='Don\'t actually query the Vision API, just generate fake tags for testing purposes.')
def run(files: Tuple[str], all: bool = False, regex: str = None, glob_pattern: str = None, max_threads: int = None,
        max_buffer: str = None, forget: bool = False, overwrite: bool = False, dry_run: bool = False,
        test: bool = False):
    """
    Run tagging on FILES.

    Files can also be selected using --all, --regex and --glob.
    --max-threads, --max-buffer-size and --forget will inherit their settings from the global config.
    """
    try:
        files = select_files(list(files), regex, glob_pattern)
    except InvalidSelectionError:
        logger.exception(InvalidSelectionError.__doc__, exc_info=False)
    else:
        client = vision.ImageAnnotatorClient()
        try:
            # Create the 'temp' directory
            if not os.path.exists(TEMP_PATH):
                logger.info("Creating temporary processing directory")
                os.makedirs(TEMP_PATH)

            with Progress("[progress.description]{task.description}", BarColumn(bar_width=None),
                          "{task.completed}/{task.total} [progress.percentage]{task.percentage:>3.0f}%") as progress:
                mp = MasterFileProcessor(files, 10, convert_to_bytes("2 MB"), True, client=client, progress=progress)
                mp.load()
                logger.info('Finished loading/starting initial threads.')
                mp.join()
                logger.info('Finished joining threads, now quitting.')
        except Exception as error:
            logger.exception(str(error))
        finally:
            os.rmdir(TEMP_PATH)
            logger.info("Temporary directory removed.")


@cli.command('collect')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.argument('output', type=click.File(mode="w"), required=False)
@click.option('--level', default=0.25)
@click.option('-a', '--all', is_flag=True, help='Add all files in the current directory to be tagged.')
@click.option('-r', '--regex', help='Use RegEx to match files in the current directory')
@click.option('-g', '--glob', 'glob_pattern', help='Use Glob (UNIX-style file pattern matching) to match files.')
def collect(files: Tuple[str], output=None, all: bool = False, regex: str = None, glob: str = None):
    """
    Collects tags from selected images for compiling the average tags of an album.

    Input is selected with FILES or using --all, --regex and --glob.
    """
    files = select_files(list(files), regex, glob)
    pass


@cli.command('auth')
@click.argument("path", type=click.Path(exists=True))
@click.option("-m", "--move", default=False, show_default=True, prompt='Move instead of copy?',
              help="Move instead of copying the credentials file", )
def auth(path: str, move: bool):
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
