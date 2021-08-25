import asyncio

import cv2
import numpy as np
import qrcode
import time
from qrcode.image.pil import PilImage
from .utils import window_is_open
import io
from prompt_toolkit import print_formatted_text,ANSI
from prompt_toolkit.shortcuts import clear
from buidl.bcur import BCURMulti

from .framebuffer import write_image_to_fb, copy_image_from_fb


def display_qr_code(data: str, name: str = "Preview") -> None:
    bc = BCURMulti(text_b64=data)
    chunks=bc.encode(animate=True)
    #return display_qr_gif(qrs_data=chunks, name=name)
    return display_qr_framebuffer(qrs_data=chunks)

def display_qr_gif(qrs_data: list, name: str = "Preview") -> None:
    # Build images to display before we show the window.
    images = [create_qr_code_image(data, animated=True) for data in qrs_data]
    images = [np.array(image.convert("RGB"))[:,:,::-1] for image in images]

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

def display_qr_ascii(qrs_data: list, name: str = "Preview") -> None:
    # Build images to display before we show the window.
    images = [create_qr_code_ascii(data) for data in qrs_data]

    finished = False
    total = len(images)
    while not finished:
        for index, image in enumerate(images):
            clear()
            print_formatted_text(ANSI(image))
            time.sleep(0.2)

def display_qr_framebuffer(qrs_data: list) -> None:

    images = [create_qr_code_image(data, animated=True) for data in qrs_data]
    images = [image.convert('RGBA') for image in images]

    if len(images) == 0:
        return

    saved = copy_image_from_fb(-100,100,images[0].width, images[0].height)

    finished = False
    try:
        while not finished:
            for image in images:
                write_image_to_fb(-100, 100, image)
                time.sleep(0.2)
    finally:
        write_image_to_fb(-100, 100, saved)


def create_qr_code_image(data: str, animated=False):
    version = 12
    fit = True  # otherwise gifs are of different sizes

    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(bytes(data, 'utf-8'))
    qr.make(fit=fit)
    image = qr.make_image(fill_color="black", back_color="white")
    return image


