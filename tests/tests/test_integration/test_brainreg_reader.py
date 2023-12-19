import pathlib


from brainglobe_napari_io.brainreg import reader_dir

brainreg_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "brainreg_output"

def test_brainreg_read_dir():
    assert reader_dir.brainreg_read_dir(str(brainreg_dir)) == reader_dir.reader_function
    assert reader_dir.brainreg_read_dir(brainreg_dir) is None
    assert reader_dir.brainreg_read_dir(str(brainreg_dir.parent)) is None

def test_load_brainreg_dir():
    layers = reader_dir.reader_function(brainreg_dir)
    assert len(layers) == 5

    layer_names = ["brain (downsampled)", "Registered image", "Hemispheres",
                   "allen_mouse_100um", "Boundaries"]

    layer_types = ["image", "image", "labels",
                   "labels", "image"]
    for idx, layer in enumerate(layers):
        assert layer[1]["name"] == layer_names[idx]
        assert layer[2] == layer_types[idx]
        assert layer[0].shape == (135, 77, 108)
