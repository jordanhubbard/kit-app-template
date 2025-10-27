#!/usr/bin/env python3
"""
Tests for per-app dependency configuration parsing and validation.
"""

import sys
from pathlib import Path
import pytest

# Add repoman tools to path
repo_root = Path(__file__).parent.parent.parent
tools_path = repo_root / "tools" / "repoman"
if str(tools_path) not in sys.path:
    sys.path.insert(0, str(tools_path))

from app_dependencies import (
    should_use_per_app_deps,
    get_app_deps_config,
    get_app_kit_path,
    get_kit_sdk_version,
    validate_deps_config,
    initialize_per_app_deps,
    create_default_deps_config,
    list_apps_with_per_app_deps
)


class TestPerAppDepsDetection:
    """Test detection of per-app dependencies."""

    def test_app_without_deps_directory_returns_false(self, test_app_path):
        """App without dependencies/ directory should not use per-app deps."""
        assert not should_use_per_app_deps(test_app_path)

    def test_app_with_deps_directory_but_no_config_returns_false(
        self, test_app_path
    ):
        """App with dependencies/ but no kit-deps.toml should return False."""
        deps_dir = test_app_path / "dependencies"
        deps_dir.mkdir()
        assert not should_use_per_app_deps(test_app_path)

    def test_app_with_deps_config_returns_true(self, test_app_with_deps_config):
        """App with dependencies/kit-deps.toml should use per-app deps."""
        assert should_use_per_app_deps(test_app_with_deps_config)

    def test_nonexistent_path_returns_false(self, tmp_path):
        """Nonexistent path should return False."""
        nonexistent = tmp_path / "does_not_exist"
        assert not should_use_per_app_deps(nonexistent)


class TestConfigParsing:
    """Test configuration file parsing."""

    def test_get_config_from_app_with_deps(self, test_app_with_deps_config):
        """Should load configuration from app with per-app deps."""
        config = get_app_deps_config(test_app_with_deps_config)
        assert config is not None
        assert 'kit_sdk' in config
        assert config['kit_sdk']['version'] == '106.0'

    def test_get_config_from_app_without_deps_returns_none(
        self, test_app_without_deps
    ):
        """Should return None for app without per-app deps."""
        config = get_app_deps_config(test_app_without_deps)
        assert config is None

    def test_get_kit_sdk_version(self, test_app_with_deps_config):
        """Should extract Kit SDK version from config."""
        version = get_kit_sdk_version(test_app_with_deps_config)
        assert version == '106.0'

    def test_get_kit_sdk_version_without_config_returns_global_default(
        self, test_app_without_deps
    ):
        """Should return global default for app without config."""
        version = get_kit_sdk_version(test_app_without_deps)
        # Should return global default from repo.toml (108.0) or fallback
        assert version is not None
        assert isinstance(version, str)


class TestKitPathResolution:
    """Test Kit SDK path resolution."""

    def test_get_app_kit_path(self, test_app_path):
        """Should return correct _kit path for app."""
        expected_path = test_app_path / "_kit"
        actual_path = get_app_kit_path(test_app_path)
        assert actual_path == expected_path

    def test_kit_path_structure(self, test_app_path):
        """Kit path should point to _kit directory in app."""
        kit_path = get_app_kit_path(test_app_path)
        assert kit_path.name == "_kit"
        assert kit_path.parent == test_app_path


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_valid_config(self):
        """Valid config should pass validation."""
        config = {
            "kit_sdk": {
                "version": "106.0"
            },
            "cache": {
                "strategy": "isolated"
            }
        }
        is_valid, error = validate_deps_config(config)
        assert is_valid
        assert error is None

    def test_validate_config_missing_kit_sdk(self):
        """Config without kit_sdk should fail validation."""
        config = {"cache": {"strategy": "isolated"}}
        is_valid, error = validate_deps_config(config)
        assert not is_valid
        assert "kit_sdk" in error

    def test_validate_config_missing_version(self):
        """Config without version should fail validation."""
        config = {"kit_sdk": {}}
        is_valid, error = validate_deps_config(config)
        assert not is_valid
        assert "version" in error

    def test_validate_config_invalid_cache_strategy(self):
        """Config with invalid cache strategy should fail."""
        config = {
            "kit_sdk": {"version": "106.0"},
            "cache": {"strategy": "invalid"}
        }
        is_valid, error = validate_deps_config(config)
        assert not is_valid
        assert "strategy" in error

    def test_validate_config_allows_shared_strategy(self):
        """Config with 'shared' strategy should be valid."""
        config = {
            "kit_sdk": {"version": "106.0"},
            "cache": {"strategy": "shared"}
        }
        is_valid, error = validate_deps_config(config)
        assert is_valid
        assert error is None


class TestConfigInitialization:
    """Test per-app dependency initialization."""

    def test_initialize_creates_dependencies_directory(self, test_app_path):
        """Initialize should create dependencies/ directory."""
        assert not (test_app_path / "dependencies").exists()
        result = initialize_per_app_deps(test_app_path)
        assert result is True
        assert (test_app_path / "dependencies").exists()

    def test_initialize_creates_kit_deps_toml(self, test_app_path):
        """Initialize should create kit-deps.toml file."""
        result = initialize_per_app_deps(test_app_path)
        assert result is True
        config_file = test_app_path / "dependencies" / "kit-deps.toml"
        assert config_file.exists()

    def test_initialize_with_custom_version(self, test_app_path):
        """Initialize should use provided Kit version."""
        result = initialize_per_app_deps(test_app_path, kit_version="107.0")
        assert result is True

        config = get_app_deps_config(test_app_path)
        assert config is not None
        assert config['kit_sdk']['version'] == '107.0'

    def test_initialize_idempotent(self, test_app_path):
        """Multiple initializations should be idempotent."""
        result1 = initialize_per_app_deps(test_app_path)
        result2 = initialize_per_app_deps(test_app_path)
        assert result1 is True
        assert result2 is True

    def test_create_default_config_structure(self):
        """Default config should have expected structure."""
        config = create_default_deps_config("106.0")
        assert 'kit_sdk' in config
        assert 'cache' in config
        assert 'dependencies' in config
        assert config['kit_sdk']['version'] == "106.0"
        assert config['cache']['strategy'] == "isolated"


class TestBackwardCompatibility:
    """Test backward compatibility with apps without per-app deps."""

    def test_app_without_config_is_backward_compatible(
        self, test_app_without_deps
    ):
        """Apps without per-app deps should work as before."""
        assert not should_use_per_app_deps(test_app_without_deps)
        assert get_app_deps_config(test_app_without_deps) is None
        # Kit version now returns global default even without per-app config
        version = get_kit_sdk_version(test_app_without_deps)
        assert version is not None  # Gets global default from repo.toml

    def test_kit_path_resolution_works_for_all_apps(self, test_app_path):
        """Kit path resolution should work regardless of per-app deps."""
        # Even without per-app deps, we can get the _kit path
        kit_path = get_app_kit_path(test_app_path)
        assert kit_path is not None
        assert kit_path.name == "_kit"


class TestAppListing:
    """Test listing apps with per-app dependencies."""

    def test_list_apps_with_per_app_deps(self, repo_root_path, tmp_path):
        """Should list all apps with per-app dependencies."""
        # Create temporary apps structure
        apps_dir = tmp_path / "source" / "apps"
        apps_dir.mkdir(parents=True)

        # App with per-app deps
        app1 = apps_dir / "app1"
        initialize_per_app_deps(app1)

        # App without per-app deps
        app2 = apps_dir / "app2"
        app2.mkdir(parents=True)

        # App with per-app deps
        app3 = apps_dir / "app3"
        initialize_per_app_deps(app3)

        # List apps
        apps = list_apps_with_per_app_deps(tmp_path)
        app_names = [app.name for app in apps]

        assert len(apps) == 2
        assert "app1" in app_names
        assert "app3" in app_names
        assert "app2" not in app_names
