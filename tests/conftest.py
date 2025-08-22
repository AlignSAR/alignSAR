import os
import numpy as np
import pytest

@pytest.fixture
def tiny_real_imag(tmp_path):
    """Create a very small R/I binary pair (3x2 float32) for RI2cpx / freadbk tests."""
    R = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.float32)
    I = np.array([[6, 5], [4, 3], [2, 1]], dtype=np.float32)
    r_path = tmp_path / "r.bin"
    i_path = tmp_path / "i.bin"
    R.tofile(r_path)
    I.tofile(i_path)
    return r_path, i_path, R, I

@pytest.fixture
def fake_safe_root(tmp_path):
    """
    Create a fake Sentinel-1 *.SAFE directory structure with annotation/ 
    and two XML files for testing get_xml_path / directory scanning functions.
    """
    safe = tmp_path / "S1A_IW_SLC__1SDV_20220109T171712_20220109T171740_041387_04EBB7_25EB.SAFE"
    anno = safe / "annotation"
    anno.mkdir(parents=True)
    (anno / "s1a-iw1-slc-vv-20220109t171712-000.xml").write_text("<xml/>")
    (anno / "s1a-iw2-slc-vh-20220109t171712-001.xml").write_text("<xml/>")
    return tmp_path  # Return parent directory containing *.SAFE

@pytest.fixture
def dates_dir(tmp_path):
    """
    Create a root directory containing 8-digit date folders for testing get_dates.
    Includes one non-date folder to test filtering.
    """
    for d in ["20220101", "20211231", "not_a_date", "20230725"]:
        p = tmp_path / d
        p.mkdir()
    return tmp_path

@pytest.fixture
def chdir_tmp(tmp_path, monkeypatch):
    """Change the current working directory to tmp_path for safer CLI/script tests."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
