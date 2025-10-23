"""
Shared pytest fixtures for CLI enhancement tests.
"""

import pytest
import shutil
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture
def cleanup_test_apps(request):
    """Clean up test applications after test execution."""
    apps_to_cleanup = []

    def register_cleanup(app_name):
        """Register an app for cleanup."""
        apps_to_cleanup.append(app_name)

    # Provide the registration function to tests
    request.instance.register_cleanup = register_cleanup if hasattr(request, 'instance') else None

    yield register_cleanup

    # Cleanup after test
    for app_name in apps_to_cleanup:
        app_path = REPO_ROOT / "source" / "apps" / app_name
        if app_path.exists():
            try:
                shutil.rmtree(app_path)
                print(f"✓ Cleaned up {app_path}")
            except Exception as e:
                print(f"Warning: Could not cleanup {app_path}: {e}")

        # Also check extensions directory
        ext_path = REPO_ROOT / "source" / "extensions" / app_name
        if ext_path.exists():
            try:
                shutil.rmtree(ext_path)
                print(f"✓ Cleaned up {ext_path}")
            except Exception as e:
                print(f"Warning: Could not cleanup {ext_path}: {e}")
