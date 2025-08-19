import json
import os
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union

import brainglobe_space as bgs
from brainglobe_atlasapi.bg_atlas import BrainGlobeAtlas
from napari.types import LayerDataTuple

from brainglobe_napari_io.brainreg.reader_dir import (
    reader_function as brainreg_reader,
)

from .utils import is_brainreg_dir

PathOrPaths = Union[List[os.PathLike], os.PathLike]


def brainreg_read_dir_sample_resolution(
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
    # registration_layers = remove_downsampled_images(registration_layers)
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


## UTILITY FUNCTIONS TO BE MOVED ELSEWHERE


def get_atlas(layers: List[LayerDataTuple]):
    for layer in layers:
        atlas = layer[1]["metadata"]["atlas_class"]
        if atlas:
            return atlas


def scale_reorient_layers(
    layers: List[LayerDataTuple], atlas, metadata
) -> List[LayerDataTuple]:
    layers = reorient_registration_layers(layers, atlas, metadata)
    layers = scale_registration_layers(layers, atlas, metadata)
    return layers


def reorient_registration_layers(
    layers: List[LayerDataTuple], atlas, metadata
) -> List[LayerDataTuple]:
    # TODO: do this with napari affine transforms, rather than transforming
    # the stack in memory
    atlas_orientation = atlas.orientation
    raw_data_orientation = metadata["orientation"]
    new_layers = []
    for layer in layers:
        new_layer = reorient_registration_layer(
            layer, atlas_orientation, raw_data_orientation
        )
        new_layers.append(new_layer)
    return new_layers


def reorient_registration_layer(
    layer: LayerDataTuple, atlas_orientation, raw_data_orientation
) -> LayerDataTuple:
    layer = list(layer)
    layer[0] = bgs.map_stack_to(
        atlas_orientation, raw_data_orientation, layer[0]
    )
    layer = tuple(layer)
    return layer


def scale_registration_layers(
    layers: List[LayerDataTuple], atlas, metadata
) -> List[LayerDataTuple]:
    new_layers = []
    scale = get_scale(atlas, metadata)
    for layer in layers:
        new_layer = scale_registration_layer(layer, scale)
        new_layers.append(new_layer)
    return new_layers


def get_scale(
    atlas, metadata, scaling_rounding_decimals: int = 5
) -> Tuple[int, ...]:
    source_space = bgs.AnatomicalSpace(metadata["orientation"])
    scaling = []
    for idx, axis in enumerate(atlas.space.axes_order):
        scaling.append(
            round(
                atlas.resolution[
                    atlas.space.axes_order.index(source_space.axes_order[idx])
                ]
                / float(metadata["voxel_sizes"][idx]),
                scaling_rounding_decimals,
            )
        )
    return tuple(scaling)


def scale_registration_layer(layer: LayerDataTuple, scale) -> LayerDataTuple:
    layer = list(layer)
    layer[1]["scale"] = scale
    layer = tuple(layer)
    return layer
