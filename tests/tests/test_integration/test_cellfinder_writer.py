import pathlib

import numpy as np
import pytest
from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO.cells import get_cells

from brainglobe_napari_io.cellfinder import reader_points, writer_points

xml_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "xml"
yml_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "yml"


@pytest.mark.parametrize("suffix", [".xml", ".yml"])
def test_points_roundrip(tmp_path, suffix):
    # Check that a read in XML/YAML file can also be written back out
    d = xml_dir if suffix == ".xml" else yml_dir
    validate_file = d / f"cell_classification{suffix}"
    layers = reader_points.points_reader(validate_file)
    assert len(layers) == 2

    test_path = str(tmp_path / f"points{suffix}")
    paths = writer_points.write_multiple_points(test_path, layers)
    assert len(paths) == 1
    assert isinstance(paths[0], str)
    if suffix == ".xml":
        assert reader_points.is_cellfinder_xml(paths[0])
    else:
        assert reader_points.is_cellfinder_yml(paths[0])

    cells_validate = get_cells(validate_file)
    cells_test = get_cells(test_path)
    assert len(cells_test) == len(cells_validate)
    assert len(cells_test) == len(set(cells_test))
    assert set(cells_test) == set(cells_validate)

    if suffix == ".yml":
        c1 = Cell((3422, 2089, 11), 1, {"Hello": "Cell"})
        c2 = Cell((1996, 3220, 2529), 2, {"Hello": "Point", "Bye": 42})
        assert c1 in cells_validate
        assert c2 in cells_validate
        assert c1 in cells_test


@pytest.mark.parametrize("suffix", [".xml", ".yml"])
def test_points_write_no_metadata(tmp_path, suffix):
    path = str(tmp_path / f"points{suffix}")
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
    writer_points.write_multiple_points(path, [points])
    cells = get_cells(path)
    assert len(cells) == 10
    assert cells[0].type == Cell.UNKNOWN


@pytest.mark.parametrize("suffix", [".xml", ".yml"])
def test_points_write_no_points(tmp_path, suffix):
    path = str(tmp_path / f"points{suffix}")
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
    assert writer_points.write_multiple_points(path, [points]) == []
