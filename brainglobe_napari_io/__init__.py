from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("brainglobe-napari-io")
except PackageNotFoundError:
    # package is not installed
    pass
