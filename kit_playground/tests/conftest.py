"""
Pytest configuration and fixtures for Kit Playground tests.
"""
import sys
from pathlib import Path

import pytest

# Add parent directories to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "kit_playground"))


@pytest.fixture
def repo_root_path():
    """Return the repository root path."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def test_project_name():
    """Return a safe test project name."""
    return "test_company.test_app"


@pytest.fixture
def malicious_project_name():
    """Return a malicious project name for security testing."""
    return "test; rm -rf /"


@pytest.fixture
def test_file_path(tmp_path):
    """Create a temporary test file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    return test_file

