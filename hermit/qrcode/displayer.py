import asyncio

import cv2
import numpy as np
import qrcode
import time
from qrcode.image.pil import PilImage
from .utils import window_is_open

from buidl.bcur import BCURMulti


def display_qr_code(data: str, name: str = "Preview") -> None:
    bc = BCURMulti(text_b64=data)
    chunks=bc.encode(animate=True)
    return display_qr_gif(qrs_data=chunks, name=name)

def display_qr_gif(qrs_data: list, name: str = "Preview") -> None:
    # Build images to display before we show the window.
    images = [create_qr_code_image(data, animated=True) for data in qrs_data]

    winname="displayqr"

    cv2.namedWindow(winname, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow(winname, 300, 300)
    cv2.setWindowProperty(winname, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    cv2.moveWindow(winname, 100, 100)

    finished = False
    total = len(images)
    try:
        while not finished:
            for index, image in enumerate(images):
                cv2.imshow(winname, image) #np.array(image.convert("RGB"))[:, :, ::-1])
                cv2.setWindowTitle(winname, f"{name}: QR Code {index+1} of {total}")

                # Allow the window to update and wait for 200ms for a keypress
                if not window_is_open(winname,200):
                    finished = True
                    break

    finally:
        cv2.destroyWindow(winname)


def create_qr_code_image(data: str, animated=False):
    version = 12
    fit = True  # otherwise gifs are of different sizes

    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(bytes(data, 'utf-8'))
    qr.make(fit=fit)
    image = qr.make_image(fill_color="black", back_color="white")

    return np.array(image.convert("RGB"))[:, :, ::-1]
