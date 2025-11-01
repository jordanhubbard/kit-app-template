import os
import pytest

if os.environ.get("PACKMAN_TESTS") != "1":
    pytest.skip("Skipping streaming (omni/Packman) tests by default", allow_module_level=True)
