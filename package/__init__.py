import os
import sys
import logging
import progressbar

# Logging and Progressbar work
progressbar.streams.wrap_stderr()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('init')
log.info('Progressbar/Logging ready.')


# Path Constants
ROOT = os.path.dirname(os.path.realpath(__file__))
INPUT_PATH = ROOT
TEMP_PATH = os.path.join(ROOT, 'temp')
OUTPUT_PATH = os.path.join(ROOT, 'output')
log.info('Path Constants Built.')

# Extension Constants
RAW_EXTS = [
    "3fr", "ari", "arw", "bay", "braw", "crw",
    "cr2", "cr3", "cap", "data", "dcs", "dcr",
    "dng", "drf", "eip", "erf", "fff", "gpr",
    "iiq", "k25", "kdc", "mdc", "mef", "mos",
    "mrw", "nef", "nrw", "obm", "orf", "pef",
    "ptx", "pxn", "r3d", "raf", "raw", "rwl",
    "rw2", "rwz", "sr2", "srf", "srw", "tif",
    "x3f",
]
LOSSY_EXTS = ["jpeg", "jpg", "png"]