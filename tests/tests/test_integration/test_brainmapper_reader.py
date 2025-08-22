import json
import pathlib

import pytest

from brainglobe_napari_io.brainmapper import brainmapper_reader_dir

brainmapper_dir = (
    pathlib.Path(__file__).parent.parent.parent / "data" / "brainmapper_output"
)
registration_dir = brainmapper_dir / "registration"

cellfinder_dir = (
    pathlib.Path(__file__).parent.parent.parent / "data" / "cellfinder_output"
)
DOWNSAMPLED_IMAGE_SIZE = (135, 108, 77)


@pytest.fixture
def metadata():
    with open(brainmapper_dir / "brainmapper.json") as json_file:
        metadata = json.load(json_file)
    return metadata


def test_is_brainmapper_dir():
    assert brainmapper_reader_dir.is_brainmapper_dir(brainmapper_dir)
    assert not brainmapper_reader_dir.is_brainmapper_dir(
        brainmapper_dir.parent
    )
    assert not brainmapper_reader_dir.is_brainmapper_dir(__file__)


def test_is_cellfinder_dir():
    assert brainmapper_reader_dir.is_brainmapper_dir(cellfinder_dir)


def test_brainmapper_read_dir():
    assert (
        brainmapper_reader_dir.brainmapper_read_dir(str(brainmapper_dir))
        == brainmapper_reader_dir.reader_function
    )
    assert brainmapper_reader_dir.brainmapper_read_dir(brainmapper_dir) is None
    assert (
        brainmapper_reader_dir.brainmapper_read_dir(
            str(brainmapper_dir.parent)
        )
        is None
    )


def check_metadata(metadata):
    assert metadata["atlas"] == "allen_mouse_100um"
    assert metadata["orientation"] == "prs"
    assert metadata["soma_diameter"] == 16


def test_get_metadata():
    check_metadata(brainmapper_reader_dir.get_metadata(brainmapper_dir))
    check_metadata(brainmapper_reader_dir.get_metadata(cellfinder_dir))


def test_load_brainmapper_dir():
    layers = brainmapper_reader_dir.reader_function(brainmapper_dir)
    assert len(layers) == 5

    layer_names = [
        "Hemispheres",
        "allen_mouse_100um",
        "Boundaries",
        "Non cells",
        "Cells",
    ]
    layer_types = ["labels", "labels", "image", "points", "points"]
    layer_shapes = [
        DOWNSAMPLED_IMAGE_SIZE,
        DOWNSAMPLED_IMAGE_SIZE,
        DOWNSAMPLED_IMAGE_SIZE,
        (22, 3),
        (103, 3),
    ]
    for idx, layer in enumerate(layers):
        assert layer[1]["name"] == layer_names[idx]
        assert layer[2] == layer_types[idx]
        assert layer[0].shape == layer_shapes[idx]


def test_load_registration(metadata):
    layers = brainmapper_reader_dir.load_registration(
        [], registration_dir, metadata
    )
    assert len(layers) == 3

    layer_names = ["Hemispheres", "allen_mouse_100um", "Boundaries"]
    for idx, layer in enumerate(layers):
        assert layer[0].shape == DOWNSAMPLED_IMAGE_SIZE
        assert layer[1]["name"] == layer_names[idx]
