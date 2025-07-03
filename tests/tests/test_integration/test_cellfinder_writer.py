import pathlib

import numpy as np
from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO.cells import get_cells

from brainglobe_napari_io.cellfinder import reader_points, writer_points

xml_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "xml"


def test_xml_roundrip(tmp_path):
    # Check that a read in XML file can also be written back out
    validate_xml_file = xml_dir / "cell_classification.xml"
    layers = reader_points.points_reader(validate_xml_file)
    assert len(layers) == 2

    test_xml_path = str(tmp_path / "points.xml")
    paths = writer_points.write_multiple_points(test_xml_path, layers)
    assert len(paths) == 1
    assert isinstance(paths[0], str)
    assert reader_points.is_cellfinder_xml(paths[0])

    cells_validate = get_cells(str(validate_xml_file))
    cells_test = get_cells(test_xml_path)
    assert len(cells_test) == len(cells_validate)
    assert cells_test[0] == cells_validate[0]
    assert cells_test[-1] == cells_validate[-1]


def test_xml_write_no_metadata(tmp_path):
    xml_path = str(tmp_path / "points.xml")
    rng = np.random.default_rng()
    points = (
        rng.random((10, 3)),
        {
            "name": "test",
            "size": 1,
            "n_dimensional": True,
            "opacity": 1,
            "symbol": "ring",
            "face_color": "lightskyblue",
            "metadata": {},
        },
        "points",
    )
    writer_points.write_multiple_points(xml_path, [points])
    cells = get_cells(xml_path)
    assert len(cells) == 10
    assert cells[0].type == Cell.UNKNOWN


def test_xml_write_no_points(tmp_path):
    xml_path = str(tmp_path / "points.xml")
    points = (
        np.array([]),
        {
            "name": "test",
            "size": 1,
            "n_dimensional": True,
            "opacity": 1,
            "symbol": "ring",
            "face_color": "lightskyblue",
            "metadata": {},
        },
        "points",
    )
    assert writer_points.write_multiple_points(xml_path, [points]) == []
