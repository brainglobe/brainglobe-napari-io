import pandas as pd
from imlib.cells.cells import Cell
from imlib.IO.cells import cells_xml_to_df


def cells_df_as_np(cells_df, new_order=[2, 1, 0], type_column="type"):
    cells_df = cells_df.drop(columns=[type_column])
    cells = cells_df[cells_df.columns[new_order]]
    cells = cells.to_numpy()
    return cells


def cells_to_array(cells):
    df = pd.DataFrame([c.to_dict() for c in cells])
    points = cells_df_as_np(df[df["type"] == Cell.CELL])
    rejected = cells_df_as_np(df[df["type"] == Cell.UNKNOWN])
    return points, rejected


def get_cell_arrays(cells_file):
    df = cells_xml_to_df(cells_file)

    non_cells = df[df["type"] == Cell.UNKNOWN]
    cells = df[df["type"] == Cell.CELL]

    cells = cells_df_as_np(cells)
    non_cells = cells_df_as_np(non_cells)
    return cells, non_cells


def convert_layer_to_cells(layer_data, cells=True):
    cells_to_save = []
    if cells:
        type = Cell.CELL
    else:
        type = Cell.UNKNOWN

    for idx, point in enumerate(layer_data):
        cell = Cell([point[2], point[1], point[0]], type)
        cells_to_save.append(cell)

    return cells_to_save


def load_cells(
    layers,
    classified_cells_path,
    point_size,
    opacity,
    symbol,
    cell_color,
    non_cell_color,
    channel=None,
):
    cells, non_cells = get_cell_arrays(str(classified_cells_path))
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
