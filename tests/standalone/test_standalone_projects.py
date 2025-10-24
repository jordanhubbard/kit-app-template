#!/usr/bin/env python3
"""
Tests for standalone project generation.

These tests verify that standalone projects can be created, built, and run
independently of the repository.
"""

import os
import pytest
import subprocess
import shutil
import tempfile
from pathlib import Path
import time

# Repository root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestStandaloneProjectCreation:
    """Test standalone project creation from templates."""

    def setup_method(self):
        """Create temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="standalone_test_"))

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_standalone_flag_creates_project(self):
        """Test that --standalone flag creates a standalone project."""
        standalone_dir = self.temp_dir / "test_standalone"

        result = subprocess.run(
            [
                "./repo.sh", "template", "new", "kit_base_editor",
                "--name", "test_standalone",
                "--output-dir", str(standalone_dir),
                "--standalone",
                "--accept-license"
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120
        )

        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")

        assert result.returncode == 0, f"Failed to create standalone project: {result.stderr}"
        assert standalone_dir.exists(), "Standalone directory not created"

    def test_standalone_structure_complete(self):
        """Verify standalone project has all required files."""
        standalone_dir = self.temp_dir / "test_structure"

        # Create standalone project
        result = subprocess.run(
            [
                "./repo.sh", "template", "new", "kit_base_editor",
                "--name", "test_structure",
                "--output-dir", str(standalone_dir),
                "--standalone",
                "--accept-license"
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120
        )

        assert result.returncode == 0

        # Verify core files exist
        assert (standalone_dir / "repo.sh").exists(), "repo.sh missing"
        assert (standalone_dir / "repo.bat").exists(), "repo.bat missing"
        assert (standalone_dir / "repo.toml").exists(), "repo.toml missing"
        assert (standalone_dir / "premake5.lua").exists(), "premake5.lua missing"
        assert (standalone_dir / "README.md").exists(), "README.md missing"

        # Verify tools exist
        assert (standalone_dir / "tools" / "packman").is_dir(), "packman directory missing"
        assert (standalone_dir / "tools" / "repoman").is_dir(), "repoman directory missing"

        # Verify application exists
        assert (standalone_dir / "source" / "apps" / "test_structure").is_dir(), "Application directory missing"
        assert (standalone_dir / "source" / "apps" / "test_structure" / "test_structure.kit").exists(), ".kit file missing"

        # Verify repo.sh is executable
        assert os.access(standalone_dir / "repo.sh", os.X_OK), "repo.sh not executable"

        print("✓ All required files present")

    def test_standalone_with_default_output_dir(self):
        """Test standalone project with default output directory."""
        # Create in current directory (use temp dir as cwd)
        result = subprocess.run(
            [
                str(REPO_ROOT / "repo.sh"), "template", "new", "kit_base_editor",
                "--name", "test_default",
                "--standalone",
                "--accept-license"
            ],
            capture_output=True,
            text=True,
            cwd=self.temp_dir,
            timeout=120
        )

        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")

        assert result.returncode == 0
        assert (self.temp_dir / "test_default").exists(), "Default output directory not created"

    def test_standalone_warns_on_existing_directory(self):
        """Test that standalone warns if directory already exists."""
        standalone_dir = self.temp_dir / "test_existing"
        standalone_dir.mkdir()

        result = subprocess.run(
            [
                "./repo.sh", "template", "new", "kit_base_editor",
                "--name", "test_existing",
                "--output-dir", str(standalone_dir),
                "--standalone",
                "--accept-license"
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120
        )

        # Template creation succeeds, but standalone generation warns
        assert result.returncode == 0, "Template creation should succeed"
        assert "Warning" in result.stderr or "already exists" in result.stderr, "Should warn about existing directory"

        # Template should be created in source/apps/ even if standalone fails
        assert (REPO_ROOT / "source" / "apps" / "test_existing").exists(), "Template should be created"


class TestStandaloneBuild:
    """Test building standalone projects."""

    def setup_method(self):
        """Create temporary directory and standalone project."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="standalone_build_"))
        self.standalone_dir = self.temp_dir / "test_build_standalone"

        # Create standalone project
        result = subprocess.run(
            [
                "./repo.sh", "template", "new", "kit_base_editor",
                "--name", "test_build_standalone",
                "--output-dir", str(self.standalone_dir),
                "--standalone",
                "--accept-license"
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120
        )

        assert result.returncode == 0, f"Failed to create standalone project: {result.stderr}"

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.slow
    def test_standalone_builds_successfully(self):
        """Test that standalone project can be built."""
        print(f"\nBuilding standalone project: {self.standalone_dir}")

        result = subprocess.run(
            ["./repo.sh", "build", "--config", "release"],
            capture_output=True,
            text=True,
            cwd=self.standalone_dir,
            timeout=600  # 10 minutes for build
        )

        print(f"Build stdout (last 1000 chars): {result.stdout[-1000:]}")
        print(f"Build stderr (last 1000 chars): {result.stderr[-1000:]}")

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Verify build output exists
        build_dir = self.standalone_dir / "_build"
        assert build_dir.exists(), "Build directory not created"

        print("✓ Standalone project built successfully")

    @pytest.mark.slow
    def test_standalone_launches_successfully(self):
        """Test that standalone project can be launched."""
        print(f"\nBuilding and launching standalone project: {self.standalone_dir}")

        # Build first
        build_result = subprocess.run(
            ["./repo.sh", "build", "--config", "release"],
            capture_output=True,
            text=True,
            cwd=self.standalone_dir,
            timeout=600
        )

        assert build_result.returncode == 0, f"Build failed: {build_result.stderr}"

        # Launch (headless)
        env = os.environ.copy()
        env["DISPLAY"] = ":99"  # Headless

        proc = subprocess.Popen(
            ["./repo.sh", "launch", "--name", "test_build_standalone.kit"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.standalone_dir,
            env=env,
            preexec_fn=os.setsid  # Process group for cleanup
        )

        try:
            # Wait for startup
            time.sleep(10)

            # Check if process is running or exited successfully
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                print(f"Launch stdout: {stdout[-1000:]}")
                print(f"Launch stderr: {stderr[-1000:]}")
                # App may exit immediately in headless - that's OK if exit code is 0 or 2
                assert proc.returncode in [0, 2], f"Launch failed with code {proc.returncode}"
            else:
                print("✓ Application started successfully")
        finally:
            # Cleanup
            import signal
            try:
                if proc.poll() is None:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                pass


class TestStandaloneIndependence:
    """Test that standalone projects are truly independent."""

    def setup_method(self):
        """Create temporary directories."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="standalone_indep_"))

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.slow
    def test_standalone_works_after_move(self):
        """Test that standalone project works after moving to different location."""
        # Create standalone project
        original_dir = self.temp_dir / "original"
        result = subprocess.run(
            [
                "./repo.sh", "template", "new", "kit_base_editor",
                "--name", "test_move",
                "--output-dir", str(original_dir),
                "--standalone",
                "--accept-license"
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120
        )

        assert result.returncode == 0

        # Move to different location
        moved_dir = self.temp_dir / "moved_location"
        shutil.move(str(original_dir), str(moved_dir))

        # Build from new location
        build_result = subprocess.run(
            ["./repo.sh", "build", "--config", "release"],
            capture_output=True,
            text=True,
            cwd=moved_dir,
            timeout=600
        )

        print(f"Build stdout (last 500 chars): {build_result.stdout[-500:]}")
        print(f"Build stderr (last 500 chars): {build_result.stderr[-500:]}")

        assert build_result.returncode == 0, f"Build failed after move: {build_result.stderr}"
        print("✓ Standalone project works after moving")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
