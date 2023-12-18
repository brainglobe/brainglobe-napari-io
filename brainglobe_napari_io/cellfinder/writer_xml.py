from typing import List

from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO.cells import save_cells
from napari.types import FullLayerData
from napari.utils.notifications import show_info

from .utils import convert_layer_to_cells


def write_multiple_points_to_xml(
    path: str, layer_data: List[FullLayerData]
) -> List[str]:
    cells_to_save = []
    for layer in layer_data:
        data, attributes, type = layer
        if "point_type" not in attributes["metadata"]:
            # Not a points layer loaded by brainglobe_napari_io
            name = attributes["name"]
            show_info(
                f'Did not find point type in metadata for "{name}" layer, '
                "Defaulting to 'Unknown'"
            )
            cells_to_save.extend(convert_layer_to_cells(data, cells=False))
        elif attributes["metadata"]["point_type"] == Cell.CELL:
            cells_to_save.extend(convert_layer_to_cells(data))
        elif attributes["metadata"]["point_type"] == Cell.UNKNOWN:
            cells_to_save.extend(convert_layer_to_cells(data, cells=False))

    if cells_to_save:
        save_cells(cells_to_save, path)
        return [path]
    else:
        return []
