from typing import Optional
from PIL import Image


class Camera:
    """Abstract base class for cameras.

    Concrete subclasses should implement the ``get_image`` method
    which should return the device's camera's current image.

    ``open`` and ``close`` methods are also available to aid with
    setup and teardown of resources associated with the device's
    camera.

    """

    def open(self) -> None:
        """Starts the camera, initializing any resources required."""
        pass

    def close(self) -> None:
        """Stops the camera, releasing any resources required."""
        pass

    def get_image(self) -> Optional[Image.Image]:
        """Get the current image from the camera.

        The image should be an instance of the `Image class
        <https://pillow.readthedocs.io/en/stable/reference/Image.html?highlight=image#the-image-class>`_
        from the `pillow library
        <(https://pillow.readthedocs.io/en/stable/>`_.

        If no image is available, return ``None``.

        """
        pass
