"""
__init__.py

The module's initialization file responsible for setting up loggers, holding a couple extension and path constants,
as well as setting up environment variables for the Google Cloud Vision API.
"""

import logging
import os

from rich.logging import RichHandler

from . import config
# noinspection PyArgumentList
from .exceptions import EmptyConfigurationValueError, InvalidConfigurationError

logging.basicConfig(
    format='[bold deep_pink2]%(threadName)s[/bold deep_pink2] %(message)s',
    level=logging.ERROR,
    handlers=[RichHandler(markup=True, rich_tracebacks=True)]
)

for loggerName in ['__init__', 'app', 'cli', 'config', 'helpers', 'process', 'xmp']:
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

# Path Constants
CWD = os.getcwd()
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
TEMP_PATH = os.path.join(CWD, "temp")
OUTPUT_PATH = os.path.join(CWD, "output")
CONFIG_PATH = os.path.join(SCRIPT_ROOT, "config")
logger.info("Path constants built successfully...")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(CONFIG_PATH, config.config["google"]["credentials"])

# Extension Constants
RAW_EXTS = ["3fr", "ari", "arw", "bay", "braw", "crw", "cr2", "cr3", "cap", "data", "dcs", "dcr", "dng", "drf", "eip",
            "erf", "fff", "gpr", "iiq", "k25", "kdc", "mdc", "mef", "mos", "mrw", "nef", "nrw", "obm", "orf", "pef",
            "ptx", "pxn", "r3d", "raf", "raw", "rwl", "rw2", "rwz", "sr2", "srf", "srw", "tif", "x3f", ]
LOSSY_EXTS = ["jpeg", "jpg", "jpe", "png"]
