import os
from pathlib import Path
from typing import List

import tifffile
from napari.types import LayerDataTuple


def is_brainreg_dir(path: os.PathLike) -> bool:
    """
    Determines whether a path is to a brainreg output directory.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        filelist = os.listdir(path)
    else:
        return False
    if "brainreg.json" in filelist:
        return True
    return False


def load_additional_downsampled_channels(
    path: Path,
    layers: List[LayerDataTuple],
    extension: str = ".tiff",
    search_string: str = "downsampled_",
    exclusion_string: str = "downsampled_standard",
) -> List[LayerDataTuple]:
    # Get additional downsampled channels, but not main one, and not those
    # in atlas space

    for file in path.iterdir():
        if (
            (file.suffix == extension)
            and file.name.startswith(search_string)
            and not file.name.startswith(exclusion_string)
        ):
            print(
                f"Found additional downsampled image: {file.name}, "
                f"adding to viewer"
            )
            name = file.name.strip(search_string).strip(extension) + (
                " (downsampled)"
            )
            layers.append(
                (
                    tifffile.imread(file),
                    {"name": name, "visible": False},
                    "image",
                )
            )

    return layers
