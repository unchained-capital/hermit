import os.path
from .errors import (
    HermitError,
    InvalidQRCodeSequence,
    InvalidPSBT,
    InvalidSignatureRequest,
    InvalidCoordinatorSignature,
)
from .config import get_config
from .wallet import HDWallet
from .signer import Signer
from .qr import (
    create_qr_sequence,
    qr_to_image,
    detect_qrs_in_image,
)
from .io import (
    display_data_as_animated_qrs,
    read_data_from_animated_qrs,
)
from .plugins import (
    load_plugins,
    plugins_loaded,
)

def _get_current_version():
    with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
        return version_file.read().strip()

__version__ = _get_current_version()
