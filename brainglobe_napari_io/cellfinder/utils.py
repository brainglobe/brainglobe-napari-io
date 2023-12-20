import os
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO.cells import cells_xml_to_df
from napari.types import LayerDataTuple


def cells_df_as_np(
    cells_df: pd.DataFrame,
    new_order: List[int] = [2, 1, 0],
    type_column: str = "type",
) -> np.ndarray:
    cells_df = cells_df.drop(columns=[type_column])
    cells = cells_df[cells_df.columns[new_order]]
    cells = cells.to_numpy()
    return cells


def get_cell_arrays(cells_file: os.PathLike) -> Tuple[np.ndarray, np.ndarray]:
    df = cells_xml_to_df(str(cells_file))

    non_cells = df[df["type"] == Cell.UNKNOWN]
    cells = df[df["type"] == Cell.CELL]

    cells = cells_df_as_np(cells)
    non_cells = cells_df_as_np(non_cells)
    return cells, non_cells


def convert_layer_to_cells(layer_data, cells: bool = True) -> List[Cell]:
    cells_to_save = []
    if cells:
        cell_type = Cell.CELL
    else:
        cell_type = Cell.UNKNOWN

    for idx, point in enumerate(layer_data):
        cell = Cell([point[2], point[1], point[0]], cell_type)
        cells_to_save.append(cell)

    return cells_to_save


def load_cells(
    layers: List[LayerDataTuple],
    classified_cells_path: Path,
    point_size: int,
    opacity: float,
    symbol: str,
    cell_color: str,
    non_cell_color: str,
    channel=None,
) -> List[LayerDataTuple]:
    cells, non_cells = get_cell_arrays(classified_cells_path)
    if channel is not None:
        channel_base = f"channel_{channel}: "
    else:
        channel_base = ""

    layers.append(
        (
            non_cells,
            {
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
