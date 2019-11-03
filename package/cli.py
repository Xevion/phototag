import logging
import click
import os
from .app import run
from . import ROOT, INPUT_PATH, OUTPUT_PATH, TEMP_PATH

@click.command()
def cli():
    print('\n'.join([os.getcwd(), ROOT, INPUT_PATH, OUTPUT_PATH, TEMP_PATH]))
    print('Executing phototag service')
    run()
    print('Phototag service executed')