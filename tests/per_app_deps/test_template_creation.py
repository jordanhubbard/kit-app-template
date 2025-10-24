#!/usr/bin/env python3
"""
Integration tests for template creation with --per-app-deps flag.
"""

import sys
import subprocess
from pathlib import Path
import pytest

repo_root = Path(__file__).parent.parent.parent


class TestTemplateCreationWithPerAppDeps:
    """Test template creation with --per-app-deps flag."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment."""
        self.repo_root = repo_root
        self.repo_script = self.repo_root / "repo.sh"

        # Ensure repo.sh exists and is executable
        if not self.repo_script.exists():
            pytest.skip("repo.sh not found")

    def cleanup_test_app(self, app_name):
        """Clean up test application."""
        app_path = self.repo_root / "source" / "apps" / app_name
        if app_path.exists():
            import shutil
            shutil.rmtree(app_path)

    @pytest.mark.slow
    def test_per_app_deps_flag_creates_dependencies_directory(self):
        """--per-app-deps flag should create dependencies/ directory."""
        app_name = "test_per_app_deps"
        self.cleanup_test_app(app_name)

        try:
            # Create app with --per-app-deps flag
            result = subprocess.run(
                [str(self.repo_script), "template", "new", "kit_base_editor",
                 app_name, "--per-app-deps", "--accept-license"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Check if command succeeded
            assert result.returncode == 0, (
                f"Template creation failed:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

            # Check if app was created
            app_path = self.repo_root / "source" / "apps" / app_name
            assert app_path.exists(), f"App not created at {app_path}"

            # Check if dependencies directory was created
            deps_dir = app_path / "dependencies"
            assert deps_dir.exists(), (
                f"dependencies/ directory not created at {deps_dir}"
            )

            # Check if kit-deps.toml was created
            config_file = deps_dir / "kit-deps.toml"
            assert config_file.exists(), (
                f"kit-deps.toml not created at {config_file}"
            )

            # Verify config content
            config_content = config_file.read_text()
            assert "kit_sdk" in config_content
            assert "version" in config_content

        finally:
            self.cleanup_test_app(app_name)

    @pytest.mark.slow
    def test_template_without_flag_no_dependencies_directory(self):
        """Template without --per-app-deps should not create dependencies/."""
        app_name = "test_no_per_app_deps"
        self.cleanup_test_app(app_name)

        try:
            # Create app without --per-app-deps flag
            result = subprocess.run(
                [str(self.repo_script), "template", "new", "kit_base_editor",
                 app_name, "--accept-license"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            assert result.returncode == 0, (
                f"Template creation failed:\n{result.stderr}"
            )

            # Check if app was created
            app_path = self.repo_root / "source" / "apps" / app_name
            assert app_path.exists()

            # Check that dependencies directory was NOT created
            deps_dir = app_path / "dependencies"
            assert not deps_dir.exists(), (
                "dependencies/ should not exist without --per-app-deps flag"
            )

        finally:
            self.cleanup_test_app(app_name)

    @pytest.mark.slow
    def test_per_app_deps_with_json_output(self):
        """--per-app-deps with --json should include flag in output."""
        app_name = "test_per_app_json"
        self.cleanup_test_app(app_name)

        try:
            # Create app with --per-app-deps and --json
            result = subprocess.run(
                [str(self.repo_script), "template", "new", "kit_base_editor",
                 app_name, "--per-app-deps", "--json", "--accept-license"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            assert result.returncode == 0

            # Parse JSON output from stderr
            import json
            json_output = None
            for line in result.stderr.split('\n'):
                if line.strip().startswith('{'):
                    try:
                        json_output = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue

            assert json_output is not None, "No JSON output found"
            assert json_output.get('per_app_deps') is True

        finally:
            self.cleanup_test_app(app_name)


class TestBackwardCompatibility:
    """Test backward compatibility of template system."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment."""
        self.repo_root = repo_root
        self.repo_script = self.repo_root / "repo.sh"

        if not self.repo_script.exists():
            pytest.skip("repo.sh not found")

    def cleanup_test_app(self, app_name):
        """Clean up test application."""
        app_path = self.repo_root / "source" / "apps" / app_name
        if app_path.exists():
            import shutil
            shutil.rmtree(app_path)

    @pytest.mark.slow
    def test_existing_templates_still_work(self):
        """Existing template creation commands should work unchanged."""
        app_name = "test_backward_compat"
        self.cleanup_test_app(app_name)

        try:
            # Use old-style template creation (no new flags)
            result = subprocess.run(
                [str(self.repo_script), "template", "new", "kit_base_editor",
                 app_name, "--accept-license"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Should succeed
            assert result.returncode == 0, (
                f"Backward compatibility broken:\n{result.stderr}"
            )

            # App should be created
            app_path = self.repo_root / "source" / "apps" / app_name
            assert app_path.exists()

        finally:
            self.cleanup_test_app(app_name)
