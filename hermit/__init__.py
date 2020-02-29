from .errors       import *
from .config       import *
from .wallet       import *
from .signer       import *
from .qrcode       import *
from .plugin       import *

import os


with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    __version__ = version_file.read().strip()
