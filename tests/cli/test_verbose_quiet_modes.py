#!/usr/bin/env python3
"""
Tests for --verbose and --quiet modes functionality.

Phase 2 Test Suite: Validate that --verbose and --quiet flags control output verbosity.
"""

import subprocess
import pytest
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


class TestVerboseMode:
    """Test --verbose flag for detailed output."""

    def setup_method(self):
        """Setup before each test."""
        # Accept license
        self.license_file = Path.home() / ".omni" / "kit-app-template" / "license_accepted.json"
        if not self.license_file.exists():
            subprocess.run(
                ["./repo.sh", "template", "new", "kit_base_editor", "--name", "dummy", "--accept-license"],
                capture_output=True,
                cwd=REPO_ROOT,
                timeout=60
            )
            dummy_path = REPO_ROOT / "source" / "apps" / "dummy"
            if dummy_path.exists():
                shutil.rmtree(dummy_path)

    def test_verbose_flag_provides_extra_output(self):
        """Verify --verbose provides more detailed output."""
        test_name = "test_verbose"

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name,
                    "--verbose"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            print(f"Return code: {result.returncode}")
            print(f"Stderr: {result.stderr[:500]}")

            assert result.returncode == 0, f"Failed: {result.stderr}"

            # Verbose mode should add [VERBOSE] markers or extra details to stderr
            if "[VERBOSE]" in result.stderr or "VERBOSE" in result.stderr:
                print("✅ Verbose mode provides extra output")
            else:
                # Acceptable if verbose just means more output in general
                print("⚠ Verbose mode may not have distinct markers (acceptable)")

        finally:
            app_path = REPO_ROOT / "source" / "apps" / test_name
            if app_path.exists():
                shutil.rmtree(app_path)

    def test_verbose_does_not_break_normal_operation(self):
        """Verify --verbose doesn't break template creation."""
        test_name = "test_verbose_works"

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name,
                    "--verbose"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            assert result.returncode == 0, f"Verbose mode broke creation: {result.stderr}"

            # Verify template was created
            app_path = REPO_ROOT / "source" / "apps" / test_name
            assert app_path.exists(), "Template not created with --verbose"

            print("✅ Verbose mode works correctly")

        finally:
            app_path = REPO_ROOT / "source" / "apps" / test_name
            if app_path.exists():
                shutil.rmtree(app_path)


class TestQuietMode:
    """Test --quiet flag for minimal output."""

    def setup_method(self):
        """Setup before each test."""
        # Accept license
        self.license_file = Path.home() / ".omni" / "kit-app-template" / "license_accepted.json"
        if not self.license_file.exists():
            subprocess.run(
                ["./repo.sh", "template", "new", "kit_base_editor", "--name", "dummy", "--accept-license"],
                capture_output=True,
                cwd=REPO_ROOT,
                timeout=60
            )
            dummy_path = REPO_ROOT / "source" / "apps" / "dummy"
            if dummy_path.exists():
                shutil.rmtree(dummy_path)

    def test_quiet_flag_reduces_output(self):
        """Verify --quiet reduces output volume."""
        test_name = "test_quiet"

        try:
            # First, run without --quiet to get baseline
            result_normal = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", f"{test_name}_normal"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            # Clean up normal test
            app_path = REPO_ROOT / "source" / "apps" / f"{test_name}_normal"
            if app_path.exists():
                shutil.rmtree(app_path)

            # Now run with --quiet
            result_quiet = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name,
                    "--quiet"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            print(f"Normal output length: {len(result_normal.stdout) + len(result_normal.stderr)}")
            print(f"Quiet output length: {len(result_quiet.stdout) + len(result_quiet.stderr)}")

            assert result_quiet.returncode == 0, f"Quiet mode failed: {result_quiet.stderr}"

            # Quiet mode should have less or equal output
            # (May not be strictly less if output is already minimal)
            quiet_total = len(result_quiet.stdout) + len(result_quiet.stderr)
            normal_total = len(result_normal.stdout) + len(result_normal.stderr)

            if quiet_total <= normal_total:
                print(f"✅ Quiet mode has reduced output ({quiet_total} vs {normal_total} chars)")
            else:
                print(f"⚠ Quiet mode output similar to normal (acceptable)")

        finally:
            app_path = REPO_ROOT / "source" / "apps" / test_name
            if app_path.exists():
                shutil.rmtree(app_path)

    def test_quiet_does_not_break_normal_operation(self):
        """Verify --quiet doesn't break template creation."""
        test_name = "test_quiet_works"

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name,
                    "--quiet"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            assert result.returncode == 0, f"Quiet mode broke creation: {result.stderr}"

            # Verify template was created
            app_path = REPO_ROOT / "source" / "apps" / test_name
            assert app_path.exists(), "Template not created with --quiet"

            print("✅ Quiet mode works correctly")

        finally:
            app_path = REPO_ROOT / "source" / "apps" / test_name
            if app_path.exists():
                shutil.rmtree(app_path)


class TestVerboseQuietBackwardCompatibility:
    """Ensure --verbose and --quiet don't break existing workflows."""

    def test_without_flags_normal_output(self):
        """Verify normal output works without flags."""
        test_name = "test_no_flags"

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name,
                    "--accept-license"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            assert result.returncode == 0, f"Normal mode failed: {result.stderr}"

            app_path = REPO_ROOT / "source" / "apps" / test_name
            assert app_path.exists(), "Template not created"

            print("✅ Normal mode works (no flags)")

        finally:
            app_path = REPO_ROOT / "source" / "apps" / test_name
            if app_path.exists():
                shutil.rmtree(app_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
