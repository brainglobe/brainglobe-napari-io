from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO.cells import get_cells
from napari.types import LayerDataTuple

# empty value we use to indicate metadata item that was not present for a cell
EMPTY_VALUE = object()


def empty_object_array(n):
    """Returns an array of the given size filled with the empty sentinel."""
    return np.full(n, EMPTY_VALUE, dtype=object)


def cells_metadata_to_arrays(
    cells: list[Cell], type: int
) -> tuple[dict[Any, np.ndarray], dict[Any, object]]:
    """
    Given a list of cells, after filtering out any cells not of the `type`, it
    returns a dictionary representing all the metadata of all the cells. This
    can be passed to napari as features of the point layer.

    The dictionary's keys are the union of all the keys of the metadata of all
    the cells. Their values are each a np object array filled with the empty
    sentinel, except for those cells who have values for the given key.

    Napari will track this in the points layer, adjusting the size of the
    arrays when new points are added/removed in the GUI. Via feature_defaults,
    napari sets new points values to the sentinel value.
    """
    cells = [c for c in cells if c.type == type]

    # any new metadata key we encounter, if we haven't seen it, we create an
    # empty array filled with the sentinel. Only those cells who have values
    # for a given key have a non-sentinel value
    data: dict = defaultdict(partial(empty_object_array, len(cells)))
    for i, cell in enumerate(cells):
        for key, value in cell.metadata.items():
            data[key][i] = value

    defaults = {key: EMPTY_VALUE for key in data.keys()}
    return data, defaults


def get_cell_arrays(all_cells: list[Cell]) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns two Nx3 and Mx3 arrays with the z,y,x position of the cells that
    are "UNKNOWN", and "CELL", respectively.
    """
    non_cells = [c for c in all_cells if c.type == Cell.UNKNOWN]
    cells = [c for c in all_cells if c.type == Cell.CELL]

    # napari expect z, y, x order
    non_cells_pos = np.array([(c.z, c.y, c.x) for c in non_cells])
    cells_pos = np.array([(c.z, c.y, c.x) for c in cells])

    return cells_pos, non_cells_pos


def convert_layer_to_cells(
    layer_data,
    cells: bool = True,
    features: dict[Any, np.ndarray] | None = None,
) -> list[Cell]:
    """
    Gets the cells from the layer.

    :param layer_data: the points from the layer.
    :param cells: Whether to mark the cells as a Cell or Unknown.
    :param features: The napari tracked features dict that stores the cell
        metadata.
    :return: The list of cells.
    """
    cells_to_save = []
    if cells:
        cell_type = Cell.CELL
    else:
        cell_type = Cell.UNKNOWN

    for idx, point in enumerate(layer_data):
        metadata = {}
        # if we have features/metadata, get the keys whose values are not
        # the empty sentinel. Features has the union of metadata keys of all
        # the cells. We want only keys that was provided for this cell.
        # When creating new points in the GUI, via feature_defaults, napari
        # initialize their metadata to the empty sentinel
        if features is not None:
            for name, arr in features.items():
                if arr[idx] is not EMPTY_VALUE:
                    metadata[name] = arr[idx]

        cell = Cell(
            [point[2], point[1], point[0]],
            cell_type,
            metadata=metadata,
        )
        cells_to_save.append(cell)

    return cells_to_save


def load_cells(
    layers: list[LayerDataTuple],
    classified_cells_path: Path,
    point_size: int,
    opacity: float,
    symbol: str,
    cell_color: str,
    non_cell_color: str,
    channel=None,
) -> list[LayerDataTuple]:
    all_cells = get_cells(str(classified_cells_path), cells_only=False)
    cells, non_cells = get_cell_arrays(all_cells)
    # napari accepts arbitrary features as a dict of arrays, we use that for
    # letting napari track the metadata of the cells
    cells_metadata, cells_metadata_defaults = cells_metadata_to_arrays(
        all_cells, Cell.CELL
    )
    non_cells_metadata, non_cells_metadata_defaults = cells_metadata_to_arrays(
        all_cells, Cell.UNKNOWN
    )

    if channel is not None:
        channel_base = f"channel_{channel}: "
    else:
        channel_base = ""

    layers.append(
        (
            non_cells,
            {
                "features": non_cells_metadata,
                "feature_defaults": non_cells_metadata_defaults,
                "name": channel_base + "Non cells",
                "size": point_size,
                "n_dimensional": True,
                "opacity": opacity,
                "symbol": symbol,
                "face_color": non_cell_color,
                "metadata": dict(point_type=Cell.UNKNOWN),
            },
            "points",
        )
    )
    layers.append(
        (
            cells,
            {
                "features": cells_metadata,
                "feature_defaults": cells_metadata_defaults,
                "name": channel_base + "Cells",
                "size": point_size,
                "n_dimensional": True,
                "opacity": opacity,
                "symbol": symbol,
                "face_color": cell_color,
                "metadata": dict(point_type=Cell.CELL),
            },
            "points",
        )
    )
    return layers
