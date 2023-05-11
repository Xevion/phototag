from phototag.cli import cli

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    logger.debug('Ready to execute CLI.')
    cli()
    logger.debug('CLI executed.')
