import FBpyGIF.fb as fb
from io import BytesIO
from PIL import Image

def copy_image_from_fb(x, y, w, h):
    (mm,fbw,fbh,bpp) = fb.ready_fb()
    bytespp = bpp//8
    s = w*bytespp

    # Allow negative x and y to place image from the right or bottom
    if x < 0:
        x = fbw + x - w

    if y < 0:
        y = fbh + y - h


    b = BytesIO()
    for z in range(h):
        fb.mmseekto(fb.vx+x, fb.vy+y+z)
        b.write(fb.mm.read(s))

    return Image.frombytes('RGBA', (w,h), b.getvalue())


def write_image_to_fb(x, y, image):
    w = image.width
    h = image.height

    (mm,fbw,fbh,bpp) = fb.ready_fb()
    bytespp = bpp//8


    # Allow negative x and y to place image from the right or bottom
    if x < 0:
        x = fbw + x - w

    if y < 0:
        y = fbh + y - h

    bytespp = bpp//8
    s = w*bytespp

    b = BytesIO(image.convert('RGBA').tobytes('raw', 'RGBA'))

    for z in range(h):
        fb.mmseekto(fb.vx+x, fb.vy+y+z)
        fb.mm.write(b.read(s))

