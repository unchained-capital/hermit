import os.path
from .errors import (
    HermitError,
    InvalidQRCodeSequence,
    InvalidPSBT,
    InvalidCoordinatorSignature,
)
from .config import get_config
from .wallet import HDWallet
from .signer import Signer
from .qr import (
    create_qr_sequence,
    qr_to_image,
    detect_qrs_in_image,
    GenericReassembler,
)
from .io import (
    display_data_as_animated_qrs,
    read_data_from_animated_qrs,
)
from .camera import Camera
from .display import Display
from .rng import (
    max_self_entropy,
    max_kolmogorov_entropy_estimate,
    max_entropy_estimate,
)
from .plugins import (
    load_plugins,
    plugins_loaded,
)


def _get_current_version():
    with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
        return version_file.read().strip()


__version__ = _get_current_version()
