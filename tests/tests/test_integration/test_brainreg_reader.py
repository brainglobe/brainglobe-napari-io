import pathlib
import shutil

import pytest

from brainglobe_napari_io.brainreg import reader_dir

brainreg_dir = (
    pathlib.Path(__file__).parent.parent.parent
    / "data"
    / "brainmapper_output"
    / "registration"
)


def test_brainreg_read_dir():
    assert (
        reader_dir.brainreg_read_dir(str(brainreg_dir))
        == reader_dir.reader_function
    )
    assert reader_dir.brainreg_read_dir(brainreg_dir) is None
    assert reader_dir.brainreg_read_dir(str(brainreg_dir.parent)) is None


@pytest.mark.parametrize("with_hemispheres", [True, False])
def test_load_brainreg_dir(tmp_path, with_hemispheres):
    directory = tmp_path / "registration"
    shutil.copytree(brainreg_dir, directory)
    if not with_hemispheres:
        (directory / "registered_hemispheres.tiff").unlink()
    layers = reader_dir.reader_function(directory)

    layer_names = [
        "brain (downsampled)",
        "Registered image",
        "Hemispheres",
        "allen_mouse_100um",
        "Boundaries",
    ]

    layer_types = ["image", "image", "labels", "labels", "image"]
    if not with_hemispheres:
        layer_names.pop(2)
        layer_types.pop(2)
    assert len(layers) == len(layer_names)
    for idx, layer in enumerate(layers):
        assert layer[1]["name"] == layer_names[idx]
        assert layer[2] == layer_types[idx]
        assert layer[0].shape == (135, 77, 108)


def test_missing_registered_atlas(tmp_path):
    directory = tmp_path / "registration"
    shutil.copytree(brainreg_dir, directory)
    (directory / "registered_hemispheres.tiff").unlink()
    (directory / "registered_atlas.tiff").unlink()

    with pytest.raises(FileNotFoundError, match="registered_atlas.tiff"):
        reader_dir.reader_function(directory)


def test_menu_calls_expected_reader(make_napari_viewer_proxy, mocker):
    make_napari_viewer_proxy()
    mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir.QFileDialog.getExistingDirectory",
        return_value=brainreg_dir,
    )
    mock_reader_hook = mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir.brainreg_read_dir",
        autospec=True,
    )

    reader_dir.select_dialog()

    mock_reader_hook.assert_called_once_with(path=str(brainreg_dir))


def test_menu_exits_gracefully(make_napari_viewer_proxy, mocker):
    make_napari_viewer_proxy()
    mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir.QFileDialog.getExistingDirectory",
        return_value="",
    )
    mock_reader_hook = mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir.brainreg_read_dir"
    )

    reader_dir.select_dialog()

    mock_reader_hook.assert_not_called()
