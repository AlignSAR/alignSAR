import pytest
from alignsar.alignsar_utils import get_dates

def test_get_dates_returns_sorted_8digit_dirs(dates_dir):
    """Check that get_dates returns only 8-digit date directories, sorted."""
    res = get_dates(str(dates_dir), master_date=None)
    assert isinstance(res, list) and len(res) >= 1

    normalized = []
    for x in res:
        if isinstance(x, str):
            assert len(x) == 8 and x.isdigit()
            normalized.append(x)
        else:
            assert hasattr(x, 'strftime')
            normalized.append(x.strftime('%Y%m%d'))

    assert normalized == sorted(normalized)
    assert "20211231" in normalized
    assert "20220101" in normalized
    assert "20230725" in normalized
