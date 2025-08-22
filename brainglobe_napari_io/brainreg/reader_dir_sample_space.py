import json
import os
from pathlib import Path
from typing import Callable, List, Optional, Union

from brainglobe_atlasapi.bg_atlas import BrainGlobeAtlas
from napari import current_viewer
from napari.types import LayerDataTuple
from qtpy.QtWidgets import QFileDialog

from brainglobe_napari_io.brainreg.reader_dir import (
    reader_function as brainreg_reader,
)
from brainglobe_napari_io.utils import (
    get_atlas_class,
    is_brainreg_dir,
    remove_downsampled_images,
    scale_reorient_layers,
)

PathOrPaths = Union[List[os.PathLike], os.PathLike]


def brainreg_read_dir_sample_space(
    path: PathOrPaths,
) -> Optional[Callable]:
    """A napari_get_reader hook specification for a reader of sample-space
    sample-resolution brainreg registration directory.

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
    """Reader function to read a brainreg registration directory in sample
    space at sample resolution.

    Original high-resolution images are expected to be loaded independently
    by the user.

    Use reader_dir_atlas_space for atlas space at atlas resolution, and
    reader_dir for sample space at atlas resolution.

    Parameters
    ----------
    path : str or list of str
        Path to brainreg registration directory.

    Returns
    -------
    layer_data : list of LayerDataTuple
        A list of LayerData tuples containing the following elements from
        brainreg registration directory:
        - Registered hemispheres label layer scaled and oriented at sample
          resolution.
        - Registered atlas label layer scaled and oriented at
          sample resolution.
        - Registered boundaries image layer scaled and oriented at sample
          resolution.
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
    """Load registration layers from a brainreg registration directory and
    scale and orient them to sample resolution.

    Parameters
    ----------
    layers : list of LayerDataTuple
        List of LayerData tuples to which the registration layers will be
        added.
    registration_directory : os.PathLike
        Path to the brainreg registration directory.
    metadata : dict
        Metadata dictionary containing information about the registration,
        including atlas information. Typically loaded from "brainreg.json"
        exported from brainreg registration.

    Returns
    -------
    layer_data : list of LayerDataTuple
        A list of LayerData tuples containing the following elements from
        brainreg registration directory:
        - Registered hemispheres label layer scaled and oriented at sample
          resolution.
        - Registered atlas label layer scaled and oriented at
          sample resolution.
        - Registered boundaries image layer scaled and oriented at sample
          resolution.
    """
    registration_layers = brainreg_reader(registration_directory)
    registration_layers = remove_downsampled_images(registration_layers)
    atlas = get_atlas_class(registration_layers)

    registration_layers = scale_reorient_layers(
        registration_layers, atlas, metadata
    )
    layers.extend(registration_layers)
    return layers


def select_dialog():
    """Open a brainreg folder selection dialog and open it in napari
    using the corresponding brainreg reader.

    This function is called via the IO Utilities submenu in Napari.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    brainreg_folder = QFileDialog.getExistingDirectory(
        caption="Select brainreg folder (sample space, sample resolution)"
    )
    if brainreg_folder:
        current_viewer().open(
            brainreg_folder,
            plugin="brainglobe-napari-io.brainreg_read_dir_sample_space",
        )
