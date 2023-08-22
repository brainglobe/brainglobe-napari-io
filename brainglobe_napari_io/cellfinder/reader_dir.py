"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the ``napari_get_reader`` hook specification, (to create
a reader plugin) but your plugin may choose to implement any of the hook
specifications offered by napari.
see: https://napari.org/docs/plugins/hook_specifications.html

Replace code below accordingly.  For complete documentation see:
https://napari.org/docs/plugins/for_plugin_developers.html
"""
import json
import os
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union

import bg_space as bgs
from napari.types import LayerDataTuple

from ..brainreg.reader_dir import reader_function as brainreg_reader
from .utils import load_cells

PathOrPaths = Union[List[os.PathLike], os.PathLike]


def is_cellfinder_dir(path: os.PathLike) -> bool:
    """
    Determines whether a path is to a cellfinder output directory.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        filelist = os.listdir(path)
    else:
        return False
    if "cellfinder.json" in filelist:
        return True
    return False


def cellfinder_read_dir(path: PathOrPaths) -> Optional[Callable]:
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
    if isinstance(path, str) and is_cellfinder_dir(path):
        return reader_function
    else:
        return None


def reader_function(
    path: os.PathLike,
    point_size: int = 15,
    opacity: float = 0.6,
    symbol: str = "ring",
) -> List[LayerDataTuple]:
    """Take a path or list of paths and return a list of LayerData tuples.

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

    print("Loading cellfinder directory")
    path = Path(os.path.abspath(path))
    with open(path / "cellfinder.json") as json_file:
        metadata = json.load(json_file)

    layers: List[LayerDataTuple] = []

    registration_directory = path / "registration"
    if registration_directory.exists():
        layers = load_registration(layers, registration_directory, metadata)

    if len(metadata["signal_planes_paths"]) > 1:
        for channel_path in path.glob("channel*"):
            channel = channel_path.name.split("_")[-1]
            layers = load_cells_from_file(
                channel_path,
                layers,
                point_size,
                opacity,
                symbol,
                channel=channel,
            )

    else:
        layers = load_cells_from_file(
            path, layers, point_size, opacity, symbol
        )

    return layers


def load_cells_from_file(
    path: Path,
    layers: List[LayerDataTuple],
    point_size: int,
    opacity: float,
    symbol: str,
    channel=None,
) -> List[LayerDataTuple]:
    classified_cells_path = path / "points" / "cell_classification.xml"
    layers = load_cells(
        layers,
        classified_cells_path,
        point_size,
        opacity,
        symbol,
        "lightgoldenrodyellow",
        "lightskyblue",
        channel=channel,
    )
    return layers


def load_registration(
    layers: List[LayerDataTuple], registration_directory: os.PathLike, metadata
) -> List[LayerDataTuple]:
    registration_layers = brainreg_reader(registration_directory)
    registration_layers = remove_downsampled_images(registration_layers)
    atlas = get_atlas(registration_layers)

    registration_layers = scale_reorient_layers(
        registration_layers, atlas, metadata
    )
    layers.extend(registration_layers)
    return layers


def get_atlas(layers: List[LayerDataTuple]):
    for layer in layers:
        atlas = layer[1]["metadata"]["atlas_class"]
        if atlas:
            return atlas


def remove_downsampled_images(
    layers: List[LayerDataTuple],
) -> List[LayerDataTuple]:
    # assumes the atlas annotations and boundaries are the last two layers
    layers = list(layers)
    return layers[-2:]


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
