from PIL import Image

from hermit import detect_qrs_in_image

def test_detect_qrs_in_image():
    image = Image.open("tests/fixtures/hello_world.jpg")
    mirror, results = detect_qrs_in_image(image)
    assert mirror is not None
    assert len(results) == 1
    assert results[0] == "Hello, world!"
