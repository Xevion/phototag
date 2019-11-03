import sys
import os
import logging
import click
from package import app

log = logging.getLogger('main')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    sys.path[0], 'package', 'key', 'photo_tagging_service.json')


@click.command()
def cli():
    log.info('Executing package...')
    sys.exit(app.run())


if __name__ == "__main__":
    main()
