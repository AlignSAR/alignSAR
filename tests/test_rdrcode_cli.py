import shutil
import subprocess
import pytest

@pytest.mark.parametrize("exe", ["rdrCode", "alignsar_utils"])
def test_cli_help_exists(exe):
    """Smoke test: check that CLI commands run and display help."""
    if shutil.which(exe) is None:
        pytest.skip(f"{exe} not in PATH (skipping)")
    p = subprocess.run([exe, "-h"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert p.returncode == 0
    out = p.stdout.lower()
    assert "usage" in out or "--help" in out
