import os
import sys

# Path Constants
ROOT = sys.path[0]
PROCESSING_PATH = os.path.join(ROOT, 'package', 'processing')
INPUT_PATH = os.path.join(PROCESSING_PATH, 'input')
TEMP_PATH = os.path.join(PROCESSING_PATH, 'temp')
OUTPUT_PATH = os.path.join(PROCESSING_PATH, 'output')

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