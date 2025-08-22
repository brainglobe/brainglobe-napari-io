import os
from pathlib import Path
from typing import List, Tuple

import brainglobe_space as bgs
import tifffile
from brainglobe_atlasapi.bg_atlas import BrainGlobeAtlas
from napari.types import LayerDataTuple


def is_brainreg_dir(path: os.PathLike) -> bool:
    """Determines whether a path is to a brainreg output directory.
    Parameters
    ----------
    path : os.PathLike
        Path to a directory.

    Returns
    -------
    bool
        True if the directory contains a brainreg.json file, False otherwise.
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
    """Load additional downsampled channels from a registration directory.

    Parameters
    ----------
    path : Path
        Path to the registration directory.
    layers : List[LayerDataTuple]
        List of layers to which the additional channels will be added.
    extension : str, optional
        File extension of the downsampled images, by default ".tiff".
    search_string : str, optional
        String to search for in the filenames of the downsampled images.
    exclusion_string : str, optional
        String to exclude from the filenames of the downsampled images.

    Returns
    -------
    List[LayerDataTuple]
        Updated list of layers with the additional downsampled channels added.
    """

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


def get_atlas_class(layers: List[LayerDataTuple]) -> str:
    """Get the atlas class from layers metadata.

    Parameters
    ----------
    layers : List[LayerDataTuple]
        List of LayerData tuples containing metadata.

    Returns
    -------
    BrainGlobeAtlas class : str
        The atlas class extracted from the metadata of the layers.
    """
    for layer in layers:
        if "metadata" in layer[1].keys():
            atlas = layer[1]["metadata"]["atlas_class"]
            return atlas

    return ""


def load_atlas(
    atlas: BrainGlobeAtlas, layers: List[LayerDataTuple]
) -> List[LayerDataTuple]:
    """Load a BrainGlobeAtlas into the layers list.

    Parameters
    ----------
    atlas : BrainGlobeAtlas
        The atlas to be loaded.
    layers : List[LayerDataTuple]
        List of LayerData tuples to which the atlas will be added.

    Returns
    -------

    List[LayerDataTuple]
        Updated list of layers with the atlas added.
    """
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


def scale_reorient_layers(
    layers: List[LayerDataTuple], atlas, metadata
) -> List[LayerDataTuple]:
    """Scale and reorient the registration layers to match
    sample scale and orientation.

    Wrapper function that applies both scaling
    and reorienting to the layers sequentially.

    Parameters
    ----------
    layers : List[LayerDataTuple]
        List of LayerData tuples containing the registration layers.
    atlas : BrainGlobeAtlas
        The atlas used for scaling and reorienting the layers.
    metadata : dict
        Metadata dictionary containing information about the registration,
        including atlas information. Typically loaded from "brainreg.json"
        exported from brainreg registration.

    Returns
    -------
    List[LayerDataTuple]
        A list of LayerData tuples containing the scaled and reoriented layers.
    """

    layers = reorient_registration_layers(layers, atlas, metadata)
    layers = scale_registration_layers(layers, atlas, metadata)
    return layers


def reorient_registration_layers(
    layers: List[LayerDataTuple], atlas, metadata
) -> List[LayerDataTuple]:
    """Reorient the registration layers to match the sample orientation.

    This function applies the reorientation on all layers based
    on the atlas orientation and the raw data orientation from the metadata.

    Parameters
    ----------
    layers : List[LayerDataTuple]
        List of LayerData tuples containing the registration layers.
    atlas : BrainGlobeAtlas
        The atlas used for reorienting the layers.
    metadata : dict
        Metadata dictionary containing information about the registration,
        including atlas information.

    Returns
    -------
    List[LayerDataTuple]
        A list of LayerData tuples containing the reoriented layers.
    """

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
    """Reorient a single registration layer to match the sample orientation.

    Parameters
    ----------
    layer : LayerDataTuple
        A single LayerData tuple containing the registration layer.
    atlas_orientation : str
        The orientation of the atlas.
    raw_data_orientation : str
        The orientation of the raw data from the metadata.

    Returns
    -------
    LayerDataTuple
        A LayerData tuple containing the reoriented layer.
    """

    layer = list(layer)
    layer[0] = bgs.map_stack_to(
        atlas_orientation, raw_data_orientation, layer[0]
    )
    layer = tuple(layer)
    return layer


def scale_registration_layers(
    layers: List[LayerDataTuple], atlas, metadata
) -> List[LayerDataTuple]:
    """Scale the registration layers to match the sample resolution.

    This function applies the scaling on all layers based on the
    atlas resolution and the raw data voxel sizes from the metadata.

    Parameters
    ----------
    layers : List[LayerDataTuple]
        List of LayerData tuples containing the registration layers.
    atlas : BrainGlobeAtlas
        The atlas used for scaling the layers.
    metadata : dict
        Metadata dictionary containing information about the registration,
        including atlas information.

    Returns
    -------
    List[LayerDataTuple]
        A list of LayerData tuples containing the scaled layers.
    """

    new_layers = []
    scale = get_scale(atlas, metadata)
    for layer in layers:
        new_layer = scale_registration_layer(layer, scale)
        new_layers.append(new_layer)
    return new_layers


def get_scale(
    atlas, metadata, scaling_rounding_decimals: int = 5
) -> Tuple[int, ...]:
    """Calculate the scaling factors to match the sample resolution.

    Parameters
    ----------
    atlas : BrainGlobeAtlas
        The atlas used for scaling.
    metadata : dict
        Metadata dictionary containing information about the registration,
        including voxel sizes of original data.
    scaling_rounding_decimals : int, optional
        Number of decimal places to round the scaling factors, by default 5.

    Returns
    -------
    Tuple[int, ...]
        A tuple containing the scaling factors for each axis
        to match the sample resolution.
    """
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
    """Scale a single registration layer to match the sample resolution.

    Scaling is performed via Napari's built-in scaling functionality,
    not by transforming the stack in memory.

    Parameters
    ----------
    layer : LayerDataTuple
        A single LayerData tuple containing the registration layer.
    scale : Tuple[int, ...]
        The scaling factors for each axis to match the sample resolution.

    Returns
    -------
    LayerDataTuple
        A LayerData tuple containing the scaled layer.
    """
    layer = list(layer)
    layer[1]["scale"] = scale
    layer = tuple(layer)
    return layer


def remove_downsampled_images(
    layers: List[LayerDataTuple],
) -> List[LayerDataTuple]:
    """Remove downsampled images from the layers list.

    Utility function to explicitly remove downsampled images
    and the registered image (which is also downsampled)
    previously loaded from a brainreg registration directory.

    Parameters
    ----------
    layers : List[LayerDataTuple]
        List of LayerData tuples containing the registration layers.

    Returns
    -------
    List[LayerDataTuple]
        A list of LayerData tuples with downsampled images removed.
    """

    # explicitly remove the downsampled images and the registered image
    # (which is also downsampled)
    # rather than assuming they are the last two layers

    return [
        layer
        for layer in layers
        if not layer[1]["name"].endswith("(downsampled)")
        and not "Registered image" == layer[1]["name"]
    ]
