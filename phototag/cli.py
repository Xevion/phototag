import logging
import click
import os

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
def auth(path):
    isrelative = click.confirm('Is this path relative to the current directory?')
    if isrelative:
        path = os.path.abspath(path)
    log.info(f'Key file location changed to "{path}"')