import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from napari.types import LayerDataTuple

from brainglobe_napari_io.brainreg.reader_dir import (
    reader_function as brainreg_reader,
)
from brainglobe_napari_io.cellfinder.utils import load_cells
from brainglobe_napari_io.utils import (
    get_atlas_class,
    remove_downsampled_images,
    scale_reorient_layers,
)

PathOrPaths = Union[List[os.PathLike], os.PathLike]


def is_brainmapper_dir(path: os.PathLike) -> bool:
    """
    Determines whether a path is to a BrainGlobe brainmapper whole brain
    cell detection (previously cellfinder) output directory.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        filelist = os.listdir(path)
    else:
        return False
    if "brainmapper.json" in filelist:
        return True
    # for backwards compatibility
    elif "cellfinder.json" in filelist:
        return True
    return False


def brainmapper_read_dir(path: PathOrPaths) -> Optional[Callable]:
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
    if isinstance(path, str) and is_brainmapper_dir(path):
        return reader_function
    else:
        return None


def get_metadata(directory: Path) -> Dict:
    try:
        with open(directory / "brainmapper.json") as json_file:
            metadata = json.load(json_file)
    # for backwards compatibility
    except FileNotFoundError:
        with open(directory / "cellfinder.json") as json_file:
            metadata = json.load(json_file)
    return metadata


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

    print("Loading brainmapper directory")
    path = Path(os.path.abspath(path))
    metadata = get_metadata(path)

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
    atlas = get_atlas_class(registration_layers)

    registration_layers = scale_reorient_layers(
        registration_layers, atlas, metadata
    )
    layers.extend(registration_layers)
    return layers
