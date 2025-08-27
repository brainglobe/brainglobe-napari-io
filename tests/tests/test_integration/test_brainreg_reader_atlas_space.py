import pathlib

from brainglobe_napari_io.brainreg import reader_dir_atlas_space

brainreg_dir = (
    pathlib.Path(__file__).parent.parent.parent
    / "data"
    / "brainmapper_output"
    / "registration"
)


def test_brainreg_read_dir_atlas_space():
    assert (
        reader_dir_atlas_space.brainreg_read_dir_atlas_space(str(brainreg_dir))
        == reader_dir_atlas_space.reader_function
    )
    assert (
        reader_dir_atlas_space.brainreg_read_dir_atlas_space(brainreg_dir)
        is None
    )
    assert (
        reader_dir_atlas_space.brainreg_read_dir_atlas_space(
            str(brainreg_dir.parent)
        )
        is None
    )


def test_load_brainreg_dir():
    layers = reader_dir_atlas_space.reader_function(brainreg_dir)
    assert len(layers) == 3

    layer_names = [
        "brain (downsampled)",
        "Registered image",
        "allen_mouse_100um",
    ]

    layer_types = ["image", "image", "labels"]
    for idx, layer in enumerate(layers):
        assert layer[1]["name"] == layer_names[idx]
        assert layer[2] == layer_types[idx]
        assert layer[0].shape == (132, 80, 114)


def test_menu_calls_expected_reader(make_napari_viewer_proxy, mocker):
    make_napari_viewer_proxy()
    mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir_atlas_space.QFileDialog.getExistingDirectory",
        return_value=brainreg_dir,
    )
    mock_reader_hook = mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir_atlas_space.brainreg_read_dir_atlas_space",
        autospec=True,
    )

    reader_dir_atlas_space.select_dialog()

    mock_reader_hook.assert_called_once_with(path=str(brainreg_dir))


def test_menu_exits_gracefully(make_napari_viewer_proxy, mocker):
    make_napari_viewer_proxy()
    mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir_atlas_space.QFileDialog.getExistingDirectory",
        return_value="",
    )
    mock_reader_hook = mocker.patch(
        "brainglobe_napari_io.brainreg.reader_dir_atlas_space.brainreg_read_dir_atlas_space"
    )

    reader_dir_atlas_space.select_dialog()

    mock_reader_hook.assert_not_called()
