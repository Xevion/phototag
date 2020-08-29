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
logging.basicConfig(
    format='%(message)s',
    level=logging.ERROR,
    handlers=[RichHandler(markup=True, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Path Constants
ROOT = os.getcwd()
INPUT_PATH = ROOT
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
TEMP_PATH = os.path.join(ROOT, "temp")
OUTPUT_PATH = os.path.join(ROOT, "output")
logger.info("Path constants built successfully...")

# Environment Variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(SCRIPT_ROOT, "config",
                                                            config.config["google"]["credentials"])

# Extension Constants
RAW_EXTS = ["3fr", "ari", "arw", "bay", "braw", "crw", "cr2", "cr3", "cap", "data", "dcs", "dcr", "dng", "drf", "eip",
            "erf", "fff", "gpr", "iiq", "k25", "kdc", "mdc", "mef", "mos", "mrw", "nef", "nrw", "obm", "orf", "pef",
            "ptx", "pxn", "r3d", "raf", "raw", "rwl", "rw2", "rwz", "sr2", "srf", "srw", "tif", "x3f", ]
LOSSY_EXTS = ["jpeg", "jpg", "jpe", "png"]
