from pathlib import Path

import numpy as np
import pandas as pd
from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO.cells import get_cells
from napari.types import LayerDataTuple


def _cells_metadata_to_df(cells: list[Cell], type: int) -> pd.DataFrame:
    return pd.DataFrame([c.metadata for c in cells if c.type == type])


def get_cell_arrays(all_cells: list[Cell]) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns two Nx3 and Mx3 arrays with the z,y,x position of the cells that
    are "UNKNOWN", and "CELL", respectively.
    """
    non_cells = [c for c in all_cells if c.type == Cell.UNKNOWN]
    cells = [c for c in all_cells if c.type == Cell.CELL]

    # napari expect z, y, x order
    non_cells_pos = np.array([(c.z, c.y, c.z) for c in non_cells])
    cells_pos = np.array([(c.z, c.y, c.z) for c in cells])

    return cells_pos, non_cells_pos


def convert_layer_to_cells(
    layer_data, cells: bool = True, features: pd.DataFrame | None = None
) -> list[Cell]:
    cells_to_save = []
    if cells:
        cell_type = Cell.CELL
    else:
        cell_type = Cell.UNKNOWN

    for idx, point in enumerate(layer_data):
        metadata = {}
        if features is not None:
            metadata = features.iloc[idx].to_dict()

        cell = Cell(
            [point[2], point[1], point[0]], cell_type, metadata=metadata
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
    # napari accepts arbitrary features as a data frame
    cells_metadata = _cells_metadata_to_df(all_cells, Cell.CELL)
    non_cells_metadata = _cells_metadata_to_df(all_cells, Cell.UNKNOWN)

    if channel is not None:
        channel_base = f"channel_{channel}: "
    else:
        channel_base = ""

    layers.append(
        (
            non_cells,
            {
                "features": non_cells_metadata,
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
