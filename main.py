import sys
import os
import logging
from package import app

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    sys.path[0], 'package', 'key', 'photo_tagging_service.json')

if __name__ == "__main__":
    logging.info('Executing package...')
    sys.exit(app.run())
