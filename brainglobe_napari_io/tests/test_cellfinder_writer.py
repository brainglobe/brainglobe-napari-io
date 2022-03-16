import pathlib

import numpy as np

from brainglobe_napari_io.cellfinder import (
    reader_xml,
    writer_xml,
)

test_data_dir = pathlib.Path(__file__) / ".." / "data"


def test_xml_roundrip(tmpdir):
    # Check that a read in XML file can also be written back out
    xml_file = test_data_dir / "cell_classification.xml"
    layers = reader_xml.xml_reader(xml_file)
    assert len(layers) == 2
    # First layer doesn't have any data, so use second layer
    layer = layers[1]

    # Test single writing
    paths = writer_xml.write_points_to_xml(
        str(tmpdir / "single.xml"), layer[0], layer[1]
    )
    assert len(paths) == 1
    assert isinstance(paths[0], str)

    # Test multiple writing
    paths = writer_xml.write_multiple_points_to_xml(
        str(tmpdir / "multiple.xml"), layers
    )
    assert len(paths) == 1
    assert isinstance(paths[0], str)
    assert reader_xml.is_cellfinder_xml(paths[0])
