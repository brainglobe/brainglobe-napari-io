import pathlib

from brainglobe_napari_io import utils

brainreg_dir = (
    pathlib.Path(__file__).parent.parent.parent
    / "data"
    / "brainmapper_output"
    / "registration"
)


def test_is_brainreg():
    assert utils.is_brainreg_dir(brainreg_dir)
    assert not utils.is_brainreg_dir(__file__)
    assert not utils.is_brainreg_dir(brainreg_dir.parent)


def test_load_additional_downsampled_channels():
    layers = utils.load_additional_downsampled_channels(brainreg_dir, [])
    assert len(layers) == 1
    assert layers[0][1]["name"] == "brain (downsampled)"
