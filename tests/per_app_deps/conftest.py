#!/usr/bin/env python3
"""
Shared pytest fixtures for per-app dependency tests.
"""

import sys
from pathlib import Path
import pytest

# Add repoman tools to path
repo_root = Path(__file__).parent.parent.parent
tools_path = repo_root / "tools" / "repoman"
if str(tools_path) not in sys.path:
    sys.path.insert(0, str(tools_path))


@pytest.fixture
def repo_root_path():
    """Get the repository root path."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def test_app_path(tmp_path):
    """Create a temporary app directory for testing."""
    app_path = tmp_path / "test_app"
    app_path.mkdir()
    return app_path


@pytest.fixture
def test_app_with_deps_config(test_app_path):
    """Create a test app with per-app dependencies configured."""
    deps_dir = test_app_path / "dependencies"
    deps_dir.mkdir()
    
    config_file = deps_dir / "kit-deps.toml"
    config_content = """
[kit_sdk]
version = "106.0"

[cache]
strategy = "isolated"

[dependencies]
"""
    config_file.write_text(config_content)
    
    return test_app_path


@pytest.fixture
def test_app_without_deps(test_app_path):
    """Create a test app without per-app dependencies (global deps)."""
    # Just return the empty app path - no dependencies/ directory
    return test_app_path

