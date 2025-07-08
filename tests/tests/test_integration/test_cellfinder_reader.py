import pathlib

import numpy as np
import pytest

from brainglobe_napari_io.cellfinder import reader_points

data_root = pathlib.Path(__file__).parent.parent.parent / "data"
xml_dir = data_root / "xml"
yml_dir = data_root / "yml"
xml_file = xml_dir / "cell_classification.xml"
yml_file = yml_dir / "cell_classification.yml"
broken_xml = xml_dir / "broken_xml.xml"
xml_with_incorrect_root_tag = xml_dir / "incorrect_tag.xml"


def test_is_cellfinder_xml():
    assert reader_points.is_cellfinder_xml(xml_file)
    assert not reader_points.is_cellfinder_xml(yml_file)
    assert not reader_points.is_cellfinder_xml(__file__)
    assert not reader_points.is_cellfinder_xml(broken_xml)
    assert not reader_points.is_cellfinder_xml(xml_with_incorrect_root_tag)


def test_is_cellfinder_yml():
    assert reader_points.is_cellfinder_yml(yml_file)
    assert not reader_points.is_cellfinder_yml(xml_file)
    assert not reader_points.is_cellfinder_yml(__file__)


@pytest.mark.parametrize("filename", [xml_file, yml_file])
def test_reader_xml(filename):
    assert (
        reader_points.cellfinder_read_points(str(filename.resolve()))
        is not None
    )
    layers = reader_points.points_reader(filename)

    assert len(layers) == 2

    for layer in layers:
        assert len(layer) == 3
        assert isinstance(layer[0], np.ndarray)
        assert isinstance(layer[1], dict)
        assert isinstance(layer[2], str)


def test_reader_no_match():
    assert reader_points.cellfinder_read_points(broken_xml) is None
