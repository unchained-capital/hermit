import asyncio

import cv2
import numpy as np
import qrcode
from qrcode.image.pil import PilImage

from .format import encode_qr_code_data
from .utils import window_is_open


def display_qr_code(data: str, name: str = "Preview") -> asyncio.Task:
    task = _display_qr_code_async(data, name)
    return asyncio.get_event_loop().create_task(task)


async def _display_qr_code_async(data: str, name: str = "Preview") -> None:
    image = create_qr_code_image(data)

    cv2.namedWindow(name)
    cv2.imshow(name, np.array(image.convert('RGB'))[:, :, ::-1].copy())

    while window_is_open(name):
        await asyncio.sleep(0.01)

    cv2.destroyWindow(name)


def create_qr_code_image(data: str) -> PilImage:

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(encode_qr_code_data(data))
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")
