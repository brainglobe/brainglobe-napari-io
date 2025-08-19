import os
from pathlib import Path
from typing import List, Tuple

import brainglobe_space as bgs
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
