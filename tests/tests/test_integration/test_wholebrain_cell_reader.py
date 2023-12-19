import pathlib
import pytest
import json
from brainglobe_napari_io.workflows import wholebrain_cell_reader_dir
from brainglobe_napari_io.brainreg.reader_dir import (
    reader_function as brainreg_reader,
)
wholebrain_cell_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "wholebrain_cell_output"
registration_dir = wholebrain_cell_dir / "registration"

DOWNSAMPLED_IMAGE_SIZE = (135, 108, 77)
@pytest.fixture
def metadata():
    with open(wholebrain_cell_dir / "cellfinder.json") as json_file:
        metadata = json.load(json_file)
    return metadata

def test_is_wholebrain_cell_dir():
    assert wholebrain_cell_reader_dir.is_wholebrain_cell_dir(wholebrain_cell_dir)
    assert not wholebrain_cell_reader_dir.is_wholebrain_cell_dir(wholebrain_cell_dir.parent)
    assert not wholebrain_cell_reader_dir.is_wholebrain_cell_dir(__file__)


def test_wholebrain_cell_read_dir():
    assert wholebrain_cell_reader_dir.wholebrain_cell_read_dir(str(wholebrain_cell_dir)) == wholebrain_cell_reader_dir.reader_function
    assert wholebrain_cell_reader_dir.wholebrain_cell_read_dir(wholebrain_cell_dir) is None
    assert wholebrain_cell_reader_dir.wholebrain_cell_read_dir(str(wholebrain_cell_dir.parent)) is None

def test_load_wholebrain_cell_dir():
    layers = wholebrain_cell_reader_dir.reader_function(wholebrain_cell_dir)
    assert len(layers) == 4

    layer_names = ["allen_mouse_100um", "Boundaries", "Non cells", "Cells"]
    layer_types = ["labels", "image", "points", "points"]
    layer_shapes = [DOWNSAMPLED_IMAGE_SIZE, DOWNSAMPLED_IMAGE_SIZE, (22, 3), (103, 3)]
    for idx, layer in enumerate(layers):
        assert layer[1]["name"] == layer_names[idx]
        assert layer[2] == layer_types[idx]
        assert layer[0].shape == layer_shapes[idx]

def test_load_registration(metadata):
    layers = wholebrain_cell_reader_dir.load_registration([], registration_dir, metadata)
    assert len(layers) == 2
    assert layers[0][0].shape == DOWNSAMPLED_IMAGE_SIZE
    assert layers[1][0].shape == DOWNSAMPLED_IMAGE_SIZE

    assert layers[0][1]["name"] == "allen_mouse_100um"
    assert layers[1][1]["name"] == "Boundaries"


