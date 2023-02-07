import json
import os
from pathlib import Path
from typing import Callable, List, Optional, Union

import tifffile
from bg_atlasapi.bg_atlas import BrainGlobeAtlas
from napari.types import LayerDataTuple

from .utils import is_brainreg_dir, load_additional_downsampled_channels

PathOrPaths = Union[List[os.PathLike], os.PathLike]


# Assume this is more used
def brainreg_read_dir(path: PathOrPaths) -> Optional[Callable]:
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """

    if isinstance(path, str) and is_brainreg_dir(path):
        return reader_function
    else:
        return None


def reader_function(path: os.PathLike) -> List[LayerDataTuple]:
    """
    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer.

        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """

    print("Loading brainreg directory")
    path = Path(os.path.abspath(path))
    with open(path / "brainreg.json") as json_file:
        metadata = json.load(json_file)

    atlas = BrainGlobeAtlas(metadata["atlas"])
    metadata["atlas_class"] = atlas

    layers: List[LayerDataTuple] = []
    layers = load_additional_downsampled_channels(path, layers)

    layers.append(
        (
            tifffile.imread(path / "downsampled.tiff"),
            {"name": "Registered image", "metadata": metadata},
            "image",
        )
    )
    layers.append(
        (
            tifffile.imread(path / "registered_hemispheres.tiff"),
            {
                "name": "Hemispheres",
                "visible": False,
                "opacity": 0.3,
            },
            "labels",
        )
    )

    layers.append(
        (
            tifffile.imread(path / "registered_atlas.tiff"),
            {
                "name": metadata["atlas"],
                "blending": "additive",
                "opacity": 0.3,
                "visible": False,
                "metadata": metadata,
            },
            "labels",
        )
    )

    layers.append(
        (
            tifffile.imread(path / "boundaries.tiff"),
            {
                "name": "Boundaries",
                "blending": "additive",
                "opacity": 0.5,
                "visible": False,
            },
            "image",
        )
    )

    return layers
