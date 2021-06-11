from napari_plugin_engine import napari_hook_implementation

from typing import List, Tuple, Dict, Any
from imlib.IO.cells import save_cells
from imlib.cells.cells import Cell

from .utils import convert_layer_to_cells


@napari_hook_implementation(specname="napari_get_writer")
def cellfinder_write_multiple_xml(path: str, layer_types: list):
    if (
        isinstance(path, str)
        and path.endswith(".xml")
        and all(item == "points" for item in layer_types)
    ):
        return write_multiple_points_to_xml
    else:
        return None


def write_multiple_points_to_xml(
    path: str, layer_data: List[Tuple[Any, Dict, str]]
) -> str:
    cells_to_save = []
    for layer in layer_data:
        data, state, type = layer
        if state["metadata"]["point_type"] == Cell.CELL:
            cells_to_save.extend(convert_layer_to_cells(data))
        elif state["metadata"]["point_type"] == Cell.UNKNOWN:
            cells_to_save.extend(convert_layer_to_cells(data, cells=False))

    if cells_to_save:
        save_cells(cells_to_save, path)

    return path
