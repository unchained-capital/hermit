import asyncio

import cv2
import numpy as np
import qrcode
import time
from qrcode.image.pil import PilImage

from .format import encode_qr_code_data
from .utils import window_is_open


def display_qr_code(data: str, name: str = "Preview") -> asyncio.Task:
    task = _display_qr_code_async(data=data, name=name)
    return asyncio.get_event_loop().create_task(task)


async def _display_qr_code_async(data: str, name: str = "Preview") -> None:
    image = create_qr_code_image(data)

    cv2.namedWindow(name)
    cv2.imshow(name, np.array(image.convert("RGB"))[:, :, ::-1].copy())

    while window_is_open(name):
        await asyncio.sleep(0.01)

    cv2.destroyWindow(name)


def display_qr_gif(qrs_data: list, name: str = "Preview") -> None:
    cv2.namedWindow(name)

    qr_idx = -1
    while True:
        _ = window_is_open(name)  # needed for some reason?

        # Increment index of which qr to show, cycling back 0 once all seen
        qr_idx += 1
        if qr_idx == len(qrs_data):
            qr_idx = 0

        print("attempting with", qr_idx, qrs_data[qr_idx])
        image = create_qr_code_image(qrs_data[qr_idx])

        cv2.imshow(name, np.array(image.convert("RGB"))[:, :, ::-1].copy())

        time.sleep(0.1)

    # TODO: better exit-condition or window-closing handling?
    cv2.destroyWindow(name)


def create_qr_code_image(data: str) -> PilImage:

    qr = qrcode.QRCode(
        version=20,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(encode_qr_code_data(decoded=data))
    qr.make(fit=False)  # fit=False because otherwise gifs are of different sizes
    return qr.make_image(fill_color="black", back_color="white")
