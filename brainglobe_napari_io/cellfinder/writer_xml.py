from napari_plugin_engine import napari_hook_implementation

from typing import List, Tuple, Dict, Any
from imlib.IO.cells import save_cells
from imlib.cells.cells import Cell

from .utils import convert_layer_to_cells


@napari_hook_implementation(specname="napari_write_points")
def cellfinder_write_xml(path, data, meta):
    if isinstance(path, str) and path.endswith(".xml"):
        return write_points_to_xml(path, data, meta)
    else:
        return None


def write_points_to_xml(path, data, metadata):
    cells_to_save = []
    if metadata["metadata"]["point_type"] == Cell.CELL:
        cells_to_save.extend(convert_layer_to_cells(data))
    elif metadata["metadata"]["point_type"] == Cell.UNKNOWN:
        cells_to_save.extend(convert_layer_to_cells(data, cells=False))

    if cells_to_save:
        save_cells(cells_to_save, path)

    return path
