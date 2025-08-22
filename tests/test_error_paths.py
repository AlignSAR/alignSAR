import numpy as np
import pytest
from alignsar.alignsar_utils import RI2cpx, freadbk

def test_RI2cpx_missing_file(tmp_path):
    """RI2cpx should raise an error when input files do not exist."""
    bad = tmp_path / "missing.bin"
    with pytest.raises((FileNotFoundError, OSError, ValueError)):
        RI2cpx(str(bad), str(bad), None, intype=np.float32)

def test_freadbk_out_of_bounds(tiny_real_imag):
    """
    freadbk should return empty or truncated data if the requested window is out of bounds.
    This checks that out-of-bounds access does not silently return a full valid array.
    """
    r_path, _, R, _ = tiny_real_imag
    arr = freadbk(
        str(r_path),
        line_start=10, pixel_start=10,  # deliberately beyond array size
        nofLines=5, nofPixels=5,
        dt='float32',
        lines=R.shape[0], pixels=R.shape[1],
        memmap=True
    )
    # For out-of-bounds, we expect either an empty array or an unexpected shape
    assert arr.size == 0 or arr.shape != (5, 5)
