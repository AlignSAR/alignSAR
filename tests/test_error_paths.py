import pytest
from alignsar.alignsar_utils import RI2cpx, freadbk

def test_RI2cpx_missing_file(tmp_path):
    """RI2cpx should raise an error when input files do not exist."""
    bad = tmp_path / "missing.bin"
    with pytest.raises((FileNotFoundError, OSError, ValueError)):
        RI2cpx(str(bad), str(bad), None, intype=np.float32)

def test_freadbk_out_of_bounds(tiny_real_imag):
    """freadbk should raise an error when requested window is out of bounds."""
    r_path, _, R, _ = tiny_real_imag
    with pytest.raises(Exception):
        _ = freadbk(
            str(r_path),
            line_start=10, pixel_start=10,
            nofLines=5, nofPixels=5,
            dt='float32',
            lines=R.shape[0], pixels=R.shape[1],
            memmap=True
        )
