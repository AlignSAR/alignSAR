import os
import pytest

from alignsar.Meta_info_extraction_global_local import get_xml_path

def test_get_xml_path_returns_annotation_dir(fake_safe_root):
    """Check that get_xml_path returns an XML file path under annotation directory."""
    base = str(fake_safe_root) + os.sep
    xml_dir = get_xml_path(base, folder_num=0, xml_num=0)
    assert isinstance(xml_dir, str)
    assert "annotation" in xml_dir
    assert os.path.isfile(xml_dir)
