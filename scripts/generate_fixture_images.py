import gzip

import numpy
import qrcode
import json
import numpy as np

import base64


from pyzbar import pyzbar
from PIL import Image

def generate_fixture_images(json_filename):
    filename_base = json_filename.split('.json')[0]
    with open(json_filename, 'r') as f:
        test_vector = json.load(f)

    data = json.dumps(test_vector['request'])
    data = data.encode('utf-8')
    data = gzip.compress(data)

    data = base64.b32encode(data)
    print(filename_base, "data length: ", len(data), " (must be <= 4296)") #
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    image.save(filename_base + '.jpg')

    #loaded_image = Image.open(filename_base + '.jpg')
    #decoded = pyzbar.decode(loaded_image)

    image_array = np.array(image.convert('RGB'))[:, :, ::-1].copy()
    numpy.save(filename_base + '.npy',image_array)

requests = ["tests/fixtures/opensource_bitcoin_test_vector_0.json"
            ]

for request in requests:
    generate_fixture_images(request)
