from pathlib import Path

from brainglobe_utils.IO.cells import is_brainglobe_xml, is_brainglobe_yaml

from .utils import load_cells


def cellfinder_read_points(path):
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
    if isinstance(path, str) and (
        is_cellfinder_xml(path) or is_cellfinder_yaml(path)
    ):
        return points_reader
    return None


def is_cellfinder_xml(path):
    path = Path(path).resolve()
    if path.suffix == ".xml":
        return is_brainglobe_xml(path)
    return False


def is_cellfinder_yaml(path):
    path = Path(path).resolve()
    if path.suffix in (".yaml", ".yml"):
        return is_brainglobe_yaml(path)
    return False


def points_reader(path, point_size=15, opacity=0.6, symbol="ring"):
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
    path = Path(path).resolve()
    print("Loading cellfinder XML/YAML points file")

    layers = []
    layers = load_cells(
        layers,
        path,
        point_size,
        opacity,
        symbol,
        "lightgoldenrodyellow",
        "lightskyblue",
    )
    return layers
