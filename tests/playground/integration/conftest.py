import os
import pytest

if os.environ.get("PACKMAN_TESTS") != "1":
    pytest.skip("Skipping playground integration (Packman) tests by default", allow_module_level=True)
