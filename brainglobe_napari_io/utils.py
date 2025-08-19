from typing import List, Tuple

import brainglobe_space as bgs
from napari.types import LayerDataTuple


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
