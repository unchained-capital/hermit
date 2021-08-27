from .base import get_qr_system
from typing import Optional

def read_qr_code() -> Optional[str]:
    return get_qr_system().read_qr_code()
