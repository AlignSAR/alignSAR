import os
import pytest

@pytest.mark.slow
@pytest.mark.skipif(os.getenv("ALIGNSAR_RUN_INTEGRATION") != "1",
                    reason="set ALIGNSAR_RUN_INTEGRATION=1 to run slow tests")
def test_signature_extraction_import_only():
    """Smoke test: ensure signature_extraction module can be imported without errors."""
    import alignsar.signature_extraction as se
    assert hasattr(se, "__file__")
