import pathlib

from brainglobe_utils.IO.cells import get_cells

from brainglobe_napari_io.cellfinder import reader_xml, writer_xml

test_data_dir = pathlib.Path(__file__).parent.parent.parent / "data"


def test_xml_roundrip(tmp_path):
    # Check that a read in XML file can also be written back out
    validate_xml_file = test_data_dir / "cell_classification.xml"
    layers = reader_xml.xml_reader(validate_xml_file)
    assert len(layers) == 2

    test_xml_path = str(tmp_path / "multiple.xml")
    paths = writer_xml.write_multiple_points_to_xml(test_xml_path, layers)
    assert len(paths) == 1
    assert isinstance(paths[0], str)
    assert reader_xml.is_cellfinder_xml(paths[0])

    cells_validate = get_cells(str(validate_xml_file))
    cells_test = get_cells(test_xml_path)
    assert len(cells_test) == len(cells_validate)
    assert cells_test[0] == cells_validate[0]
    assert cells_test[-1] == cells_validate[-1]
