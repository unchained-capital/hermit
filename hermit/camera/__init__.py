from os import environ
from .base import Camera

#
# Ordinarily we don't want to import these classes because their
# dependencies might not be installed.
#
# The `IO` class handles loading the proper class based on the
# configured camera mode.
#
# This environment variable exists to force load all camera classes so
# they can be included in documentation.
#

if environ.get("HERMIT_LOAD_ALL_IO"):
    from .opencv import OpenCVCamera
    from .imageio import ImageIOCamera
