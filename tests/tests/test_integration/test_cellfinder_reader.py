import pathlib

import numpy as np

from brainglobe_napari_io.cellfinder import reader_xml

xml_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "xml"
xml_file = xml_dir / "cell_classification.xml"
broken_xml = xml_dir / "broken_xml.xml"
xml_with_incorrect_root_tag = xml_dir / "incorrect_tag.xml"


def test_is_cellfinder_xml():
    assert reader_xml.is_cellfinder_xml(xml_file)
    assert not reader_xml.is_cellfinder_xml(__file__)
    assert not reader_xml.is_cellfinder_xml(broken_xml)
    assert not reader_xml.is_cellfinder_xml(broken_xml)
    assert not reader_xml.is_cellfinder_xml(xml_with_incorrect_root_tag)


def test_reader_xml():
    assert reader_xml.cellfinder_read_xml(str(xml_file.resolve())) is not None
    layers = reader_xml.xml_reader(xml_file)

    assert len(layers) == 2

    for layer in layers:
        assert len(layer) == 3
        assert isinstance(layer[0], np.ndarray)
        assert isinstance(layer[1], dict)
        assert isinstance(layer[2], str)
