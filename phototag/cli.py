"""
cli.py

The file responsible for providing commandline functionality to the user.
"""

import logging
import os
import shutil

import click

from . import config

log = logging.getLogger("cli")


@click.group()
def cli():
    """Base CLI command group"""
    pass


@cli.command()
def run():
    """Run tagging of all valid files in the current directory."""
    log.info(f"CLI started tagging at {os.getcwd()}")
    from .app import run

    run()


@cli.command()
@click.argument("path")
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
            log.warning("The specified path is a directory, not a file.")
        else:
            log.warning("The specified path does not exist.")
    else:
        # Identify the final location of the file in the config directory
        _, head = os.path.split(path)
        new_path = os.path.join(config.SCRIPT_ROOT, "config", head)

        # Move or copy the file
        if move:
            shutil.move(path, new_path)
            log.info("Successfully moved file to configuration file...")
        elif not move:
            shutil.copy(path, new_path)
            log.info("Successfully copied file to configuration folder...")

        # Update the configuration file to point to the
        config.config["google"]["credentials"] = head
        config.quicksave()

        log.info(f"Configuration updated.")
