import numpy as np
import pytest

from alignsar.alignsar_utils import RI2cpx, freadbk

def test_RI2cpx_basic_roundtrip(tiny_real_imag, tmp_path):
    """Check RI2cpx output matches the given R/I arrays and writes a valid complex file."""
    r_path, i_path, R, I = tiny_real_imag
    out_cpx = tmp_path / "out.cpx"
    cpx = RI2cpx(str(r_path), str(i_path), str(out_cpx), intype=np.float32)

    assert cpx.dtype == np.complex64
    assert cpx.size == R.size
    assert np.allclose(cpx.real.reshape(R.shape), R)
    assert np.allclose(cpx.imag.reshape(I.shape), I)
    assert out_cpx.exists()
    loaded = np.fromfile(out_cpx, dtype=np.complex64)
    assert np.allclose(loaded, cpx)

def test_freadbk_full_slice(tiny_real_imag):
    """Check freadbk reads the full array correctly."""
    r_path, _, R, _ = tiny_real_imag
    arr = freadbk(
        str(r_path),
        line_start=1,
        pixel_start=1,
        nofLines=R.shape[0],
        nofPixels=R.shape[1],
        dt='float32',
        lines=R.shape[0],
        pixels=R.shape[1],
        memmap=True
    )
    assert arr.shape == R.shape
    assert np.allclose(arr, R)

def test_freadbk_subwindow(tiny_real_imag):
    """Check freadbk reads a subwindow of the array correctly."""
    r_path, _, R, _ = tiny_real_imag
    arr = freadbk(
        str(r_path),
        line_start=2,
        pixel_start=2,
        nofLines=2,
        nofPixels=1,
        dt='float32',
        lines=R.shape[0],
        pixels=R.shape[1],
        memmap=True
    )
    assert arr.shape == (2, 1)
    expected = R[1:, 1:2]
    assert np.allclose(arr, expected)
