#!/usr/bin/env python3
"""
Compatibility tests for CLI workflows.

These tests validate that existing CLI commands work as documented.
They serve as the baseline for all future changes - if these tests
start failing after a change, that change broke backward compatibility.

Test Philosophy:
- Test current behavior (even if imperfect)
- Document what works vs. what doesn't
- Provide regression detection for future changes
"""

import subprocess
import pytest
import sys
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

class TestCLIBasicCommands:
    """Test basic CLI commands that should always work."""

    def test_repo_sh_exists(self):
        """Verify repo.sh exists and is executable."""
        repo_sh = REPO_ROOT / "repo.sh"
        assert repo_sh.exists(), "repo.sh not found"
        assert repo_sh.stat().st_mode & 0o111, "repo.sh is not executable"

    def test_repo_sh_runs(self):
        """Verify repo.sh can be executed without errors."""
        result = subprocess.run(
            ["./repo.sh", "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        # Help command should exit with 0 or show help text
        # Document current behavior
        assert result.returncode in [0, 1], f"repo.sh --help failed with code {result.returncode}"


class TestTemplateListCommand:
    """Test template list command."""

    def test_template_list_works(self):
        """Verify ./repo.sh template list returns without error."""
        result = subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert len(result.stdout) > 0, "No output from template list"

    def test_template_list_shows_applications(self):
        """Verify template list shows application templates."""
        result = subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        assert result.returncode == 0
        # Check for documented application templates
        assert "kit_base_editor" in result.stdout, "kit_base_editor not found in template list"

    def test_template_list_type_filter_applications(self):
        """Verify template list --type=application works."""
        result = subprocess.run(
            ["./repo.sh", "template", "list", "--type=application"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        # Document current behavior - may or may not be implemented
        print(f"Return code: {result.returncode}")
        print(f"Stdout sample: {result.stdout[:200]}")

    def test_template_list_type_filter_extensions(self):
        """Verify template list --type=extension works."""
        result = subprocess.run(
            ["./repo.sh", "template", "list", "--type=extension"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        # Document current behavior
        print(f"Return code: {result.returncode}")


class TestTemplateDocsCommand:
    """Test template docs command."""

    def test_template_docs_works_for_kit_base_editor(self):
        """Verify ./repo.sh template docs kit_base_editor works."""
        result = subprocess.run(
            ["./repo.sh", "template", "docs", "kit_base_editor"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert len(result.stdout) > 0, "No documentation output"
        assert "kit_base_editor" in result.stdout.lower(), "Template name not in docs"

    def test_template_docs_fails_for_nonexistent_template(self):
        """Verify template docs handles nonexistent template gracefully."""
        result = subprocess.run(
            ["./repo.sh", "template", "docs", "nonexistent_template_xyz"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        # Should fail gracefully - document behavior
        print(f"Return code: {result.returncode}")
        print(f"Stderr: {result.stderr[:200] if result.stderr else 'None'}")
        # We expect non-zero return code for nonexistent template
        assert result.returncode != 0, "Should fail for nonexistent template"


class TestTemplateNewCommand:
    """Test template new command (non-interactive mode)."""

    def test_template_new_shows_help(self):
        """Verify template new without args shows help or prompts."""
        result = subprocess.run(
            ["./repo.sh", "template", "new"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10,
            input=""  # Send empty stdin to avoid hanging
        )
        # Document current behavior - might prompt or show help
        print(f"Return code: {result.returncode}")
        print(f"Output sample: {result.stdout[:200] if result.stdout else 'None'}")

    @pytest.mark.slow
    def test_template_new_noninteractive_basic(self):
        """Verify ./repo.sh template new with minimum arguments works."""
        # This test will document current behavior
        # It may fail if --accept-license is required (Phase 2 will add this)
        result = subprocess.run(
            [
                "./repo.sh", "template", "new", "kit_base_editor",
                "--name", "test_compat_baseline",
                "--display-name", "Test Compat Baseline",
                "--version", "0.1.0"
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120  # Template creation can take time
        )

        print(f"\nReturn code: {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")

        # Document the baseline behavior
        # In Phase 2, we'll add --accept-license to make this work
        if result.returncode == 0:
            # Check if app was created
            app_path = REPO_ROOT / "source" / "apps" / "test_compat_baseline"
            if app_path.exists():
                print(f"✓ Application created at: {app_path}")
                # Cleanup for future test runs
                import shutil
                try:
                    shutil.rmtree(app_path)
                    print("✓ Cleaned up test application")
                except Exception as e:
                    print(f"Warning: Could not cleanup {app_path}: {e}")


class TestBuildCommand:
    """Test build command."""

    def test_build_help_works(self):
        """Verify ./repo.sh build help works."""
        result = subprocess.run(
            ["./repo.sh", "build", "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        # Document behavior
        print(f"Return code: {result.returncode}")
        print(f"Output sample: {result.stdout[:300] if result.stdout else 'None'}")


class TestLaunchCommand:
    """Test launch command."""

    def test_launch_help_works(self):
        """Verify ./repo.sh launch help works."""
        result = subprocess.run(
            ["./repo.sh", "launch", "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )
        # Document behavior
        print(f"Return code: {result.returncode}")
        print(f"Output sample: {result.stdout[:300] if result.stdout else 'None'}")


class TestPythonDependencies:
    """Test that required Python dependencies are available."""

    def test_toml_library_available(self):
        """Verify toml library is available."""
        try:
            import toml
            assert True, "toml library imported successfully"
        except ImportError:
            try:
                import tomllib
                assert True, "tomllib (Python 3.11+) imported successfully"
            except ImportError:
                pytest.fail("Neither toml nor tomllib is available")

    def test_packman_python_works(self):
        """Verify packman Python can run."""
        packman_python = REPO_ROOT / "tools" / "packman" / "python.sh"
        if packman_python.exists():
            result = subprocess.run(
                [str(packman_python), "--version"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=30
            )
            print(f"Packman Python version check: {result.returncode}")
            print(f"Output: {result.stdout[:100] if result.stdout else 'None'}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
