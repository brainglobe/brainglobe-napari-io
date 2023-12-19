import pathlib

import numpy as np
import pytest
from brainglobe_utils.cells.cells import Cell

from brainglobe_napari_io.cellfinder import utils

xml_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "xml"
xml_file = xml_dir / "cell_classification.xml"


@pytest.fixture
def cell_layers():
    layers = utils.load_cells(
        [],
        xml_file,
        1,
        1,
        "disk",
        "lightgoldenrodyellow",
        "lightskyblue",
    )
    return layers


@pytest.fixture
def cell_layers_channel_6():
    layers = utils.load_cells(
        [],
        xml_file,
        1,
        1,
        "disk",
        "lightgoldenrodyellow",
        "lightskyblue",
        channel=6,
    )
    return layers


def test_load_cells(cell_layers):
    assert len(cell_layers) == 2

    for layer in cell_layers:
        assert len(layer) == 3
        assert isinstance(layer[0], np.ndarray)
        assert isinstance(layer[1], dict)
        assert isinstance(layer[2], str)

        assert layer[2] == "points"

    assert cell_layers[0][1]["name"] == "Non cells"
    assert cell_layers[1][1]["name"] == "Cells"

    assert cell_layers[0][1]["metadata"]["point_type"] == Cell.UNKNOWN
    assert cell_layers[1][1]["metadata"]["point_type"] == Cell.CELL

    assert len(cell_layers[0][0]) == 22
    assert len(cell_layers[1][0]) == 103


def test_load_cells_with_channel(cell_layers_channel_6):
    assert len(cell_layers_channel_6) == 2
    assert cell_layers_channel_6[0][1]["name"] == "channel_6: Non cells"
    assert cell_layers_channel_6[1][1]["name"] == "channel_6: Cells"


def test_convert_layer_to_cells(cell_layers):
    cells = utils.convert_layer_to_cells(cell_layers[0][0])
    assert len(cells) == 22
    assert isinstance(cells[0], Cell)
    assert cells[0].type == Cell.CELL

    cells = utils.convert_layer_to_cells(cell_layers[0][0], cells=False)
    assert len(cells) == 22
    assert isinstance(cells[0], Cell)
    assert cells[0].type == Cell.UNKNOWN
