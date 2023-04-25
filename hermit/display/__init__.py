from os import environ
from .base import Display

#
# Ordinarily we don't want to import these classes because their
# dependencies might not be installed.
#
# The `IO` class handles loading the proper class based on the
# configured display mode.
#
# This environment variable exists to force load all display classes
# so they can be included in documentation.
#

if environ.get("HERMIT_LOAD_ALL_IO"):
    from .ascii import ASCIIDisplay
    from .framebuffer import FrameBufferDisplay
    from .opencv import OpenCVDisplay
