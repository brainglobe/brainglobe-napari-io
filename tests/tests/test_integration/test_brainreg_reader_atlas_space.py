import pathlib


from brainglobe_napari_io.brainreg import reader_dir_atlas_space

brainreg_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "brainreg_output"

def test_brainreg_read_dir_atlas_space():
    assert reader_dir_atlas_space.brainreg_read_dir_atlas_space(str(brainreg_dir)) == reader_dir_atlas_space.reader_function
    assert reader_dir_atlas_space.brainreg_read_dir_atlas_space(brainreg_dir) is None
    assert reader_dir_atlas_space.brainreg_read_dir_atlas_space(str(brainreg_dir.parent)) is None

def test_load_brainreg_dir():
    layers = reader_dir_atlas_space.reader_function(brainreg_dir)
    assert len(layers) == 3

    layer_names = ["brain (downsampled)", "Registered image", "allen_mouse_100um"]

    layer_types = ["image", "image", "labels"]
    for idx, layer in enumerate(layers):
        assert layer[1]["name"] == layer_names[idx]
        assert layer[2] == layer_types[idx]
        assert layer[0].shape == (132, 80, 114)
