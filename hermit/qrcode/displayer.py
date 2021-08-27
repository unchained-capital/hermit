from .base import get_qr_system

def display_qr_code(data: str) -> None:
    return get_qr_system().display_qr_code(data)
