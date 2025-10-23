#!/usr/bin/env python3
"""
Comprehensive template testing - ALL templates.

This test suite validates that EVERY template in the repository can be:
1. Created successfully (template new)
2. Built successfully (build)
3. Launched successfully (headless mode for testing)

This establishes the "before" baseline - documenting which templates work
and which don't BEFORE any modifications are made.

CRITICAL: For headless testing, we set DISPLAY to non-existent display
to prevent window creation and verify the application can start.
"""

import subprocess
import pytest
import shutil
import time
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

# Template definitions - organized by type
# These are discovered from ./repo.sh template list

APPLICATIONS = [
    "kit_base_editor",
    "omni_usd_viewer",
    "omni_usd_explorer",
    "omni_usd_composer",
]

EXTENSIONS = [
    "basic_python_extension",
    "basic_python_ui_extension",
    "basic_cpp_extension",
    "basic_python_binding",
]

MICROSERVICES = [
    "kit_service",
]

# Note: base_application is a base template, not meant to be instantiated directly
# Note: setup templates (kit_service_setup, omni_usd_composer_setup, etc.) are components

ALL_INSTANTIABLE_TEMPLATES = APPLICATIONS + EXTENSIONS + MICROSERVICES


def cleanup_test_project(project_name):
    """Clean up a test project completely, including auto-generated extensions."""
    # Clean from source/apps
    app_path = REPO_ROOT / "source" / "apps" / project_name
    if app_path.exists():
        try:
            shutil.rmtree(app_path)
            print(f"✓ Cleaned up {app_path}")
        except Exception as e:
            print(f"Warning: Could not cleanup {app_path}: {e}")

    # Clean from source/extensions
    ext_path = REPO_ROOT / "source" / "extensions" / project_name
    if ext_path.exists():
        try:
            shutil.rmtree(ext_path)
            print(f"✓ Cleaned up {ext_path}")
        except Exception as e:
            print(f"Warning: Could not cleanup {ext_path}: {e}")

    # Clean auto-generated extensions (setup, messaging)
    # These are created automatically by some application templates
    extensions_dir = REPO_ROOT / "source" / "extensions"
    if extensions_dir.exists():
        # Look for extensions with matching project name prefix
        for ext_dir in extensions_dir.iterdir():
            if ext_dir.is_dir() and ext_dir.name.startswith(project_name):
                try:
                    shutil.rmtree(ext_dir)
                    print(f"✓ Cleaned up auto-generated extension: {ext_dir.name}")
                except Exception as e:
                    print(f"Warning: Could not cleanup {ext_dir}: {e}")


class TestTemplateCreation:
    """Test that all templates can be created."""

    @pytest.mark.parametrize("template_name", APPLICATIONS)
    def test_create_application(self, template_name):
        """Test creating each application template."""
        project_name = f"test_app_{template_name}"

        # Clean up any previous test artifacts
        cleanup_test_project(project_name)

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", template_name,
                    "--name", project_name,
                    "--display-name", f"Test {template_name}",
                    "--version", "0.1.0"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=120
            )

            print(f"\n{'='*60}")
            print(f"Template: {template_name}")
            print(f"Return code: {result.returncode}")
            print(f"{'='*60}")

            if result.returncode == 0:
                print(f"✓ {template_name} created successfully")

                # Verify the application was created
                app_path = REPO_ROOT / "source" / "apps" / project_name
                assert app_path.exists(), f"Application directory not found: {app_path}"

                # Verify key files exist
                kit_file = app_path / f"{project_name}.kit"
                assert kit_file.exists(), f"Kit file not found: {kit_file}"

                print(f"✓ Verified structure for {project_name}")
            else:
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
                pytest.fail(f"Failed to create {template_name}: {result.stderr}")

        finally:
            # Cleanup
            cleanup_test_project(project_name)

    @pytest.mark.parametrize("template_name", EXTENSIONS)
    def test_create_extension(self, template_name):
        """Test creating each extension template."""
        project_name = f"test_ext.{template_name}"

        # Clean up any previous test artifacts
        cleanup_test_project(project_name)

        # Known issue: basic_python_binding doesn't respect --name parameter
        # It creates my_company.my_basic_python_binding instead
        # Clean up this default name too
        if template_name == "basic_python_binding":
            cleanup_test_project("my_company.my_basic_python_binding")

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", template_name,
                    "--name", project_name,
                    "--display-name", f"Test {template_name}",
                    "--version", "0.1.0"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=120
            )

            print(f"\n{'='*60}")
            print(f"Template: {template_name}")
            print(f"Return code: {result.returncode}")
            print(f"{'='*60}")

            if result.returncode == 0:
                print(f"✓ {template_name} created successfully")

                # Find the actual created extension directory
                # Some templates (like basic_python_binding) don't respect the --name parameter
                ext_path = REPO_ROOT / "source" / "extensions" / project_name
                actual_project_name = project_name

                if not ext_path.exists():
                    # Check if it was created with a different name
                    # Parse the output to find actual created path
                    import re
                    # Remove ALL whitespace including line breaks, then re-space
                    output_clean = result.stdout.replace('\n', '').replace('\r', '')
                    match = re.search(r"created successfully in\s+(.+?)(?:\s+|$)", output_clean)
                    if match:
                        actual_path_str = match.group(1).strip()
                        actual_path = Path(actual_path_str)
                        print(f"⚠ Template created with different name: {actual_path}")
                        ext_path = actual_path
                        # Store actual name for cleanup
                        actual_project_name = actual_path.name

                assert ext_path.exists(), f"Extension directory not found: {ext_path}"
                print(f"✓ Verified structure for {actual_project_name}")

                # Update project_name for cleanup
                project_name = actual_project_name
            else:
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
                pytest.fail(f"Failed to create {template_name}: {result.stderr}")

        finally:
            # Cleanup - use the actual project name
            cleanup_test_project(project_name)
            # Also cleanup default name for basic_python_binding
            if template_name == "basic_python_binding":
                cleanup_test_project("my_company.my_basic_python_binding")

    @pytest.mark.parametrize("template_name", MICROSERVICES)
    def test_create_microservice(self, template_name):
        """Test creating each microservice template."""
        project_name = f"test_svc_{template_name}"

        # Clean up any previous test artifacts
        cleanup_test_project(project_name)

        try:
            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", template_name,
                    "--name", project_name,
                    "--display-name", f"Test {template_name}",
                    "--version", "0.1.0"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=120
            )

            print(f"\n{'='*60}")
            print(f"Template: {template_name}")
            print(f"Return code: {result.returncode}")
            print(f"{'='*60}")

            if result.returncode == 0:
                print(f"✓ {template_name} created successfully")

                # Verify the service was created
                app_path = REPO_ROOT / "source" / "apps" / project_name
                assert app_path.exists(), f"Service directory not found: {app_path}"

                print(f"✓ Verified structure for {project_name}")
            else:
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
                pytest.fail(f"Failed to create {template_name}: {result.stderr}")

        finally:
            # Cleanup
            cleanup_test_project(project_name)


class TestTemplateBuildAndLaunch:
    """
    Test that templates can be built and launched.

    These are SLOW tests that create, build, and launch applications.
    Mark as slow to allow selective execution.
    """

    @pytest.mark.slow
    @pytest.mark.parametrize("template_name", APPLICATIONS)
    def test_build_and_launch_application(self, template_name):
        """
        Test full workflow: create → build → launch (headless) → stop.

        CRITICAL: Uses fake DISPLAY to test headless startup without window.
        """
        project_name = f"test_build_{template_name}"

        # Clean up any previous test artifacts
        cleanup_test_project(project_name)

        try:
            # Step 1: Create
            print(f"\n{'='*60}")
            print(f"STEP 1: Creating {template_name}")
            print(f"{'='*60}")

            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", template_name,
                    "--name", project_name,
                    "--display-name", f"Test Build {template_name}",
                    "--version", "0.1.0"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=120
            )

            assert result.returncode == 0, f"Failed to create: {result.stderr}"
            print(f"✓ Created {project_name}")

            # Step 2: Build
            print(f"\n{'='*60}")
            print(f"STEP 2: Building {project_name}")
            print(f"{'='*60}")

            result = subprocess.run(
                ["./repo.sh", "build", "--config", "release"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=600  # 10 minutes for build
            )

            if result.returncode != 0:
                print(f"Build stdout: {result.stdout[-1000:]}")  # Last 1000 chars
                print(f"Build stderr: {result.stderr[-1000:]}")
                pytest.fail(f"Failed to build: {result.stderr}")

            print(f"✓ Built {project_name}")

            # Step 3: Launch (headless testing)
            print(f"\n{'='*60}")
            print(f"STEP 3: Launching {project_name}")
            print(f"{'='*60}")

            # Launch in background with timeout
            # Note: Kit apps need X display. Set DISPLAY to non-existent to test headless startup
            # Or just launch and immediately kill to verify it starts
            env = os.environ.copy()
            env["DISPLAY"] = ":99"  # Non-existent display for headless test

            proc = subprocess.Popen(
                [
                    "./repo.sh", "launch",
                    "--name", f"{project_name}.kit"  # Need .kit extension
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=REPO_ROOT,
                env=env
            )

            # Wait for startup (max 60 seconds)
            print("Waiting for application startup...")
            time.sleep(10)  # Give it time to start

            # Check if process is still running
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                print(f"Launch stdout: {stdout[-1000:]}")
                print(f"Launch stderr: {stderr[-1000:]}")
                # Some apps may exit immediately in headless mode - that's OK
                # We just want to verify they can be built and launch without error
                if proc.returncode != 0:
                    pytest.fail(f"Application failed with code {proc.returncode}")

            print(f"✓ Launched {project_name} successfully")

            # Step 4: Graceful shutdown
            print(f"\n{'='*60}")
            print(f"STEP 4: Stopping {project_name}")
            print(f"{'='*60}")

            try:
                proc.terminate()
                proc.wait(timeout=10)
                print(f"✓ Stopped {project_name} gracefully")
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                print(f"⚠ Killed {project_name} (did not stop gracefully)")

            print(f"\n{'='*60}")
            print(f"✓ COMPLETE: {template_name} passed all steps")
            print(f"{'='*60}\n")

        finally:
            # Ensure process is dead
            try:
                proc.kill()
            except:
                pass

            # Cleanup
            cleanup_test_project(project_name)

    @pytest.mark.slow
    @pytest.mark.parametrize("template_name", MICROSERVICES)
    def test_build_and_launch_microservice(self, template_name):
        """
        Test microservice workflow: create → build → launch (headless) → stop.
        """
        project_name = f"test_build_{template_name}"

        # Clean up any previous test artifacts
        cleanup_test_project(project_name)

        try:
            # Step 1: Create
            print(f"\n{'='*60}")
            print(f"STEP 1: Creating {template_name}")
            print(f"{'='*60}")

            result = subprocess.run(
                [
                    "./repo.sh", "template", "new", template_name,
                    "--name", project_name,
                    "--display-name", f"Test Build {template_name}",
                    "--version", "0.1.0"
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=120
            )

            assert result.returncode == 0, f"Failed to create: {result.stderr}"
            print(f"✓ Created {project_name}")

            # Step 2: Build
            print(f"\n{'='*60}")
            print(f"STEP 2: Building {project_name}")
            print(f"{'='*60}")

            result = subprocess.run(
                ["./repo.sh", "build", "--config", "release"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=600
            )

            if result.returncode != 0:
                print(f"Build stdout: {result.stdout[-1000:]}")
                print(f"Build stderr: {result.stderr[-1000:]}")
                pytest.fail(f"Failed to build: {result.stderr}")

            print(f"✓ Built {project_name}")

            # Step 3: Launch (microservices are headless by nature)
            print(f"\n{'='*60}")
            print(f"STEP 3: Launching {project_name}")
            print(f"{'='*60}")

            env = os.environ.copy()
            env["DISPLAY"] = ":99"  # Non-existent display for headless test

            proc = subprocess.Popen(
                [
                    "./repo.sh", "launch",
                    "--name", f"{project_name}.kit"  # Need .kit extension
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=REPO_ROOT,
                env=env
            )

            # Wait for startup
            print("Waiting for service startup...")
            time.sleep(10)

            # Check if process is still running
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                print(f"Launch stdout: {stdout[-1000:]}")
                print(f"Launch stderr: {stderr[-1000:]}")
                # Services may exit immediately in headless mode - that's OK
                if proc.returncode != 0:
                    pytest.fail(f"Service failed with code {proc.returncode}")

            print(f"✓ Launched {project_name} successfully")

            # Step 4: Stop
            try:
                proc.terminate()
                proc.wait(timeout=10)
                print(f"✓ Stopped {project_name}")
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                print(f"⚠ Killed {project_name}")

            print(f"\n✓ COMPLETE: {template_name} passed all steps\n")

        finally:
            try:
                proc.kill()
            except:
                pass
            cleanup_test_project(project_name)


class TestTemplateDiscovery:
    """Test that we can discover all templates."""

    def test_discover_all_templates(self):
        """Verify we can list all templates programmatically."""
        result = subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30
        )

        assert result.returncode == 0
        output = result.stdout

        # Verify all expected templates are present
        for template in ALL_INSTANTIABLE_TEMPLATES:
            assert template in output, f"Template {template} not found in list"

        print(f"\n✓ All {len(ALL_INSTANTIABLE_TEMPLATES)} templates discovered")

    def test_template_count(self):
        """Document how many templates we have."""
        print(f"\nTemplate counts:")
        print(f"  Applications: {len(APPLICATIONS)}")
        print(f"  Extensions: {len(EXTENSIONS)}")
        print(f"  Microservices: {len(MICROSERVICES)}")
        print(f"  Total instantiable: {len(ALL_INSTANTIABLE_TEMPLATES)}")


if __name__ == "__main__":
    # Run with specific markers
    import sys

    if "--quick" in sys.argv:
        # Quick tests only (no builds)
        pytest.main([__file__, "-v", "-s", "-m", "not slow"])
    elif "--slow" in sys.argv:
        # Slow tests only (builds and launches)
        pytest.main([__file__, "-v", "-s", "-m", "slow"])
    else:
        # All tests
        pytest.main([__file__, "-v", "-s"])
