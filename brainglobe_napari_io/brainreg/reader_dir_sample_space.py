import json
import os
from pathlib import Path
from typing import Callable, List, Optional, Union

from brainglobe_atlasapi.bg_atlas import BrainGlobeAtlas
from napari.types import LayerDataTuple

from brainglobe_napari_io.brainreg.reader_dir import (
    reader_function as brainreg_reader,
)
from brainglobe_napari_io.utils import (
    get_atlas,
    is_brainreg_dir,
    scale_reorient_layers,
)

PathOrPaths = Union[List[os.PathLike], os.PathLike]


def brainreg_read_dir_sample_space(
    path: PathOrPaths,
) -> Optional[Callable]:
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

    path = Path(os.path.abspath(path))
    with open(path / "brainreg.json") as json_file:
        metadata = json.load(json_file)

    atlas = BrainGlobeAtlas(metadata["atlas"])
    metadata["atlas_class"] = atlas
    layers: List[LayerDataTuple] = []

    layers = load_registration(layers, path, metadata)

    return layers


def load_registration(
    layers: List[LayerDataTuple], registration_directory: os.PathLike, metadata
) -> List[LayerDataTuple]:
    registration_layers = brainreg_reader(registration_directory)
    atlas = get_atlas(registration_layers)

    registration_layers = scale_reorient_layers(
        registration_layers, atlas, metadata
    )
    layers.extend(registration_layers)
    return layers


def load_atlas(
    atlas: BrainGlobeAtlas, layers: List[LayerDataTuple]
) -> List[LayerDataTuple]:
    atlas_image = atlas.annotation
    layers.append(
        (
            atlas_image,
            {
                "name": atlas.atlas_name,
                "visible": False,
                "blending": "additive",
                "opacity": 0.3,
            },
            "labels",
        )
    )

    return layers
