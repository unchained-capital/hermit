from pyzbar import pyzbar
from PIL import ImageOps
from PIL.ImageDraw import ImageDraw


def detect_qrs_in_image(image, box_width=2):
    """
    Return frame, [data_str1, data_str2, ...]

    The returned frame is the original frame with a green box
    drawn around each of the identified QR codes.
    """
    barcodes = pyzbar.decode(image)

    annotate = ImageDraw(image)

    # Mark the qr codes in the image
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        annotate.rectangle([(x, y), (x + w, y + h)], outline="#00FF00", width=box_width)

    # Return the mirror image of the annoted original
    mirror = ImageOps.mirror(image)

    # Extract qr code data
    results = [barcode.data.decode("utf-8").strip() for barcode in barcodes]

    return mirror, results
