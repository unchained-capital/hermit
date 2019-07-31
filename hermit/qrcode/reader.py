from typing import Optional


from pyzbar import pyzbar
import asyncio
import cv2


from hermit.errors import InvalidSignatureRequest
from .format import decode_qr_code_data
from .utils import window_is_open


def read_qr_code() -> Optional[str]:
    task = _capture_qr_code_async()
    return asyncio.get_event_loop().run_until_complete(task)


async def _capture_qr_code_async() -> Optional[str]:
    capture = _start_camera()
    preview_dimensions = (640, 480)
    decoded_data = None
    encoded_data = None
    window_name = "Signature Request QR Code Scanner"
    cv2.namedWindow(window_name)

    while window_is_open(window_name):
        ret, frame = capture.read()
        frame = cv2.resize(frame, preview_dimensions)

        for qrcode in pyzbar.decode(frame):
            # Extract the position & dimensions of box bounding the QR
            # code
            (x, y, w, h) = qrcode.rect
            # Draw this bounding box on the image
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2)

            # Decode the QR code data
            encoded_data = qrcode.data
            try:
                decoded_data = decode_qr_code_data(encoded_data)
            except InvalidSignatureRequest as e:
                print("Invalid signature request: {}".format(str(e)))

            # Use the first QR code found
            if decoded_data is not None:
                break

        # Preview the (reversed) frame
        mirror = cv2.flip(frame, 1)
        cv2.imshow(window_name, mirror)

        # Break out of the loop if we found a valid QR code
        if decoded_data:
            break

        await asyncio.sleep(0.01)

    # Clean up windows before exiting.
    capture.release()
    cv2.destroyWindow(window_name)

    return decoded_data


def _start_camera() -> cv2.VideoCapture:
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        raise IOError("Cannot open webcam")
    return capture
