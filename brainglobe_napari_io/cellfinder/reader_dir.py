"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the ``napari_get_reader`` hook specification, (to create
a reader plugin) but your plugin may choose to implement any of the hook
specifications offered by napari.
see: https://napari.org/docs/plugins/hook_specifications.html

Replace code below accordingly.  For complete documentation see:
https://napari.org/docs/plugins/for_plugin_developers.html
"""
import os
import sys
import json
import bg_space as bgs
from pathlib import Path
from napari_plugin_engine import napari_hook_implementation

from ..brainreg.reader_dir import reader_function as brainreg_reader

from .utils import load_cells


def is_cellfinder_dir(path):
    """Determines whether a path is to a brainreg output directory

    Parameters
    ----------
    path : str
        Path to file.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        filelist = os.listdir(path)
    else:
        return False
    if "cellfinder.json" in filelist:
        return True
    return False


@napari_hook_implementation(specname="napari_get_reader")
def cellfinder_read_dir(path):
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


def reader_function(path, point_size=15, opacity=0.6, symbol="ring"):
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

    layers = []

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
    path, layers, point_size, opacity, symbol, channel=None
):
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


def load_registration(layers, registration_directory, metadata):
    registration_layers = brainreg_reader(registration_directory)
    registration_layers = remove_downsampled_images(registration_layers)
    atlas = get_atlas(registration_layers)

    registration_layers = scale_reorient_layers(
        registration_layers, atlas, metadata
    )
    layers.extend(registration_layers)
    return layers


def get_atlas(layers):
    for layer in layers:
        atlas = layer[1]["metadata"]["atlas_class"]
        if atlas:
            return atlas


def remove_downsampled_images(layers):
    # assumes the atlas annotations and boundaries are the last two layers
    layers = list(layers)
    layers = layers[-2:]
    layers = tuple(layers)
    return layers


def scale_reorient_layers(layers, atlas, metadata):
    layers = reorient_registration_layers(layers, atlas, metadata)
    layers = scale_registration_layers(layers, atlas, metadata)
    return layers


def reorient_registration_layers(layers, atlas, metadata):
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
    layer, atlas_orientation, raw_data_orientation
):
    layer = list(layer)
    layer[0] = bgs.map_stack_to(
        atlas_orientation, raw_data_orientation, layer[0]
    )
    layer = tuple(layer)
    return layer


def scale_registration_layers(layers, atlas, metadata):
    new_layers = []
    scale = get_scale(atlas, metadata)
    for layer in layers:
        new_layer = scale_registration_layer(layer, scale)
        new_layers.append(new_layer)
    return new_layers


def get_scale(atlas, metadata, scaling_rounding_decimals=5):
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


def scale_registration_layer(layer, scale):
    layer = list(layer)
    layer[1]["scale"] = scale
    layer = tuple(layer)
    return layer
