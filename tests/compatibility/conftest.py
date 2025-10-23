"""
Pytest configuration for compatibility tests.
"""

import pytest
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

@pytest.fixture
def repo_root():
    """Provide repository root path to tests."""
    return REPO_ROOT

@pytest.fixture
def cleanup_test_apps(request):
    """Cleanup test applications after test runs."""
    apps_to_cleanup = []

    def add_cleanup(app_name):
        apps_to_cleanup.append(app_name)

    # Provide the add_cleanup function to tests
    request.instance.add_cleanup = add_cleanup if hasattr(request, 'instance') else lambda x: None

    yield

    # Cleanup after test
    import shutil
    for app_name in apps_to_cleanup:
        app_path = REPO_ROOT / "source" / "apps" / app_name
        if app_path.exists():
            try:
                shutil.rmtree(app_path)
                print(f"✓ Cleaned up test app: {app_name}")
            except Exception as e:
                print(f"Warning: Could not cleanup {app_name}: {e}")
