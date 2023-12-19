import pathlib

import numpy as np
from brainglobe_utils.cells.cells import Cell

from brainglobe_napari_io.cellfinder import reader_xml

test_data_dir = pathlib.Path(__file__) / ".." / "data"


def test_reader_xml():
    # Basic smoke tests for the XML reader
    xml_file = test_data_dir / "cell_classification.xml"
    assert reader_xml.is_cellfinder_xml(xml_file)
    assert not reader_xml.is_cellfinder_xml(__file__)
    assert reader_xml.cellfinder_read_xml(str(xml_file.resolve())) is not None
    layers = reader_xml.xml_reader(xml_file)

    assert len(layers) == 2

    for layer in layers:
        assert len(layer) == 3
        assert isinstance(layer[0], np.ndarray)
        assert isinstance(layer[1], dict)
        assert isinstance(layer[2], str)

        assert layer[2] == "points"

    assert layers[0][1]["name"] == "Non cells"
    assert layers[1][1]["name"] == "Cells"

    assert layers[0][1]["metadata"]["point_type"] == Cell.UNKNOWN
    assert layers[1][1]["metadata"]["point_type"] == Cell.CELL

    assert len(layers[0][0]) == 22
    assert len(layers[1][0]) == 103
