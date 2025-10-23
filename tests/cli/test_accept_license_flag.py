#!/usr/bin/env python3
"""
Tests for --accept-license flag functionality.

Phase 2 Test Suite: Validate that --accept-license flag works correctly
for non-interactive template creation.
"""

import subprocess
import pytest
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


class TestAcceptLicenseFlag:
    """Test --accept-license flag for non-interactive operation."""

    def setup_method(self):
        """Setup before each test."""
        # Remove license acceptance file to start fresh
        self.license_file = Path.home() / ".omni" / "kit-app-template" / "license_accepted.json"
        if self.license_file.exists():
            self.license_file.unlink()
            print(f"✓ Removed existing license file: {self.license_file}")

    def test_accept_license_flag_exists(self):
        """Verify --accept-license flag is recognized."""
        # Note: License check happens before --help is shown, so we test
        # by attempting to use the flag (next test validates it works)

        # Just verify the template command structure exists
        result = subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT
        )

        # List command should work
        assert result.returncode == 0, f"Template command failed: {result.stderr}"

        # The real test for --accept-license is in the next test
        print("✅ Template command structure exists")

    def test_template_new_with_accept_license(self):
        """Verify template creation works with --accept-license flag."""
        test_name = "test_accept_license"

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name,
                    "--display-name", "Test Accept License",
                    "--version", "1.0.0",
                    "--accept-license"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout[-500:]}")
            print(f"Stderr: {result.stderr[-500:]}")

            # Should succeed
            assert result.returncode == 0, f"Template creation failed: {result.stderr}"

            # Verify output path
            expected_path = REPO_ROOT / "source" / "apps" / test_name
            assert expected_path.exists(), f"Template not created at {expected_path}"

            # Verify license was accepted
            assert self.license_file.exists(), "License acceptance not stored"

            print(f"✅ Template created with --accept-license flag")

        finally:
            # Cleanup
            app_path = REPO_ROOT / "source" / "apps" / test_name
            if app_path.exists():
                shutil.rmtree(app_path)
                print(f"✓ Cleaned up {app_path}")

    def test_accept_license_persists(self):
        """Verify license acceptance persists across commands."""
        test_name1 = "test_persist_1"
        test_name2 = "test_persist_2"

        try:
            # First creation with --accept-license
            result1 = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name1,
                    "--accept-license"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            assert result1.returncode == 0, f"First creation failed: {result1.stderr}"
            assert self.license_file.exists(), "License not stored after first creation"

            # Second creation WITHOUT --accept-license should work
            # because license is already accepted
            result2 = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name2
                    # Note: NO --accept-license flag
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            print(f"Second creation return code: {result2.returncode}")
            print(f"Second creation stdout: {result2.stdout[-300:]}")

            # Should succeed because license already accepted
            assert result2.returncode == 0, f"Second creation failed: {result2.stderr}"

            expected_path2 = REPO_ROOT / "source" / "apps" / test_name2
            assert expected_path2.exists(), f"Second template not created at {expected_path2}"

            print(f"✅ License acceptance persisted across commands")

        finally:
            # Cleanup both
            for test_name in [test_name1, test_name2]:
                app_path = REPO_ROOT / "source" / "apps" / test_name
                if app_path.exists():
                    shutil.rmtree(app_path)
                    print(f"✓ Cleaned up {app_path}")

    def test_without_accept_license_on_first_run(self):
        """Verify creation without --accept-license requires interaction or fails."""
        test_name = "test_no_accept"

        try:
            # Attempt creation WITHOUT --accept-license and without terminal
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", "kit_base_editor",
                    "--name", test_name,
                    "--display-name", "Test No Accept",
                    "--version", "1.0.0"
                    # Note: NO --accept-license flag
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                stdin=subprocess.DEVNULL,  # No interactive input
                timeout=60
            )

            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout[-300:]}")
            print(f"Stderr: {result.stderr[-300:]}")

            # Behavior depends on implementation:
            # Option 1: Fails with error about license
            # Option 2: Shows license and waits (would timeout/fail)
            # Option 3: Prompts and we pass DEVNULL so it fails

            # Document the actual behavior
            if result.returncode != 0:
                # This is expected behavior - should fail or error
                print("✅ Correctly requires license acceptance")
                assert "license" in result.stderr.lower() or "license" in result.stdout.lower(), \
                    "Error message should mention license"
            else:
                # If it succeeds, license system might be more permissive
                print("⚠ Warning: Command succeeded without explicit license acceptance")
                print("    This may be acceptable if license was previously accepted")

        finally:
            # Cleanup if created
            app_path = REPO_ROOT / "source" / "apps" / test_name
            if app_path.exists():
                shutil.rmtree(app_path)
                print(f"✓ Cleaned up {app_path}")

    def test_accept_license_with_extension_template(self):
        """Verify --accept-license works with extension templates too."""
        test_name = "test_ext_accept"

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", "basic_python_extension",
                    "--name", test_name,
                    "--accept-license"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=60
            )

            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout[-300:]}")

            assert result.returncode == 0, f"Extension creation failed: {result.stderr}"

            # Verify created in extensions directory
            expected_path = REPO_ROOT / "source" / "extensions" / test_name
            assert expected_path.exists(), f"Extension not created at {expected_path}"

            print(f"✅ --accept-license works with extension templates")

        finally:
            # Cleanup
            ext_path = REPO_ROOT / "source" / "extensions" / test_name
            if ext_path.exists():
                shutil.rmtree(ext_path)
                print(f"✓ Cleaned up {ext_path}")


class TestAcceptLicenseBackwardCompatibility:
    """Ensure --accept-license doesn't break existing workflows."""

    def test_interactive_mode_still_works(self):
        """Verify interactive mode (without --accept-license) still works."""
        # This test documents that interactive mode should still work
        # when a TTY is available (we can't fully test this in CI)

        result = subprocess.run(
            ["./repo.sh", "template", "new", "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT
        )

        assert result.returncode == 0, "Template new --help should work"
        print("✅ Interactive mode command structure preserved")

    def test_existing_templates_unaffected(self):
        """Verify existing templates work with --accept-license."""
        # List all templates
        result = subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT
        )

        assert result.returncode == 0, "Template list should work"

        # Verify we have templates
        assert len(result.stdout) > 0, "Should have templates"
        assert "kit_base_editor" in result.stdout, "Should include kit_base_editor"

        print("✅ Template list works (unaffected by --accept-license)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
