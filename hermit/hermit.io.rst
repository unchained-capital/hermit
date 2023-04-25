Input & Output
==============

In addition to text input and output, Hermit requires input and output
of animated sequences of QR codes.

Hermit has several different modes for both input (camera) and output
(display) of these sequences.

Cameras
-------

Hermit defines an abstract ``Camera`` class which defines an API
for capturing QR code images from the device's camera.

Different camera modes correspond to ``Camera`` subclasses which
provide specific implementations for this API.

.. autoclass:: hermit.camera.Camera
    :members:

Camera Modes
~~~~~~~~~~~~

Hermit's default camera mode (``opencv``) is implemented by the
``OpenCVCamera`` class:

.. autoclass:: hermit.camera.OpenCVCamera

The following ``Camera`` subclasses are also provided:

.. autoclass:: hermit.camera.ImageIOCamera


Displays
--------

Hermit defines an abstract ``Display`` class which defines an API for
displaying

1. a sequence of animated QR code images on the device's screen

2. a real-time image of what the camera is seeing (for aid in scanning
   QR codes).

Different display modes correspond to ``Display`` subclasses which
provide specific implementations for this API.

.. autoclass:: hermit.display.Display
    :members:

Display Modes
~~~~~~~~~~~~~

Hermit's default display mode (``opencv``) is implemented by the
``OpenCVDisplay`` class:

.. autoclass:: hermit.display.OpenCVDisplay

The following ``Display`` subclasses are also provided:

.. autoclass:: hermit.display.ASCIIDisplay
.. autoclass:: hermit.display.FrameBufferDisplay
