import logging
import click
import shutil
import sys
import os

from . import config

log = logging.getLogger('cli')

@click.group()
def cli():
    pass

@cli.command()
def run():
    log.info(f'CLI started tagging at {os.getcwd()}')
    from .app import run
    run()

@cli.command()
@click.argument('path')
@click.option('-m', '--move', default=False, show_default=True, prompt=True, help='Move instead of copying the credentials file')
def auth(path, move):
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    # Verify that the file eixsts
    if os.path.isfile(path):
        log.info('Specifed path is file and exists')
    else:
        if os.path.isdir(path):
            log.warning('Specified path is directory, not file!')
        else:
            log.warning('Specified path doesn\'t exist!')
        log.warning('Please correct the path before trying again.')
        click.exit()
    # Identify the final location of the file in the config directory
    _, head = os.path.split(path)
    new_path = os.path.join(config.SCRIPT_ROOT, 'config', head)
    # MOVE the file
    if move:
        shutil.move(path, new_path)
        log.info('Successfully moved file to configuration file.')
    # COPY the file
    elif not move:
        # May be something to think about - should we copy metadata, permissions, etc? Probably not.
        shutil.copy(path, new_path)
        log.info('Successfully copied file to configuration folder.')
    config.config['google']['credentials'] = head
    config.quicksave()
    log.info(f'Key file configuration updated.')