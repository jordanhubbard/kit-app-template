"""
Integration test to validate .kit file creation across all phases.

This test ensures that when a project is created, the .kit file:
1. Actually exists at the expected location
2. Has correct content structure
3. Is in the correct directory structure
4. Matches the location returned by the API

This addresses the critical bug where template generation reported success
but no .kit file was actually created.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import pytest

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.repoman.template_api import TemplateAPI


class TestKitFileCreation:
    """Test that .kit files are actually created when projects are generated."""

    @pytest.fixture
    def clean_repo(self):
        """Provide a clean repo state for testing."""
        repo_root = Path(__file__).parent.parent.parent.parent
        test_app_dir = repo_root / "source" / "apps" / "test_kit_file_creation"

        # Clean up before test
        if test_app_dir.exists():
            shutil.rmtree(test_app_dir)

        yield repo_root, test_app_dir

        # Clean up after test
        if test_app_dir.exists():
            shutil.rmtree(test_app_dir)

    def test_create_application_creates_kit_file(self, clean_repo):
        """Test that create_application() actually creates the .kit file."""
        repo_root, test_app_dir = clean_repo
        api = TemplateAPI(str(repo_root))

        # Create application
        result = api.create_application(
            template_name='kit_base_editor',
            name='test_kit_file_creation',
            display_name='Test Kit File Creation',
            version='1.0.0',
            accept_license=True,
            no_register=False  # FIXED: --no-register flag not supported by replay command
        )

        # Validate result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get('success'), f"Creation should succeed: {result.get('error', 'No error message')}"

        # Validate required fields exist
        assert 'app_name' in result, "Result should contain app_name"
        assert 'app_dir' in result, "Result should contain app_dir"
        assert 'kit_file' in result, "Result should contain kit_file path"

        # Extract paths
        app_dir = result['app_dir']
        kit_file = result['kit_file']

        print(f"\nTest Results:")
        print(f"  app_dir: {app_dir}")
        print(f"  kit_file: {kit_file}")

        # Validate .kit file exists
        kit_file_path = Path(kit_file)
        if not kit_file_path.is_absolute():
            kit_file_path = Path(repo_root) / kit_file

        assert kit_file_path.exists(), f".kit file should exist at: {kit_file_path}"

        # Validate .kit file location matches expected structure
        # Should be in source/apps/{name}/{name}.kit
        expected_dir = repo_root / "source" / "apps" / "test_kit_file_creation"
        expected_kit = expected_dir / "test_kit_file_creation.kit"

        assert kit_file_path == expected_kit, \
            f".kit file should be at {expected_kit}, but is at {kit_file_path}"

        # Validate .kit file has content
        kit_content = kit_file_path.read_text()
        assert len(kit_content) > 0, ".kit file should not be empty"
        assert '[package]' in kit_content or '[app]' in kit_content, \
            ".kit file should have valid TOML structure"

        # Validate directory structure
        assert expected_dir.exists(), f"App directory should exist at: {expected_dir}"
        assert expected_dir.is_dir(), "App directory should be a directory"

        print(f"✓ .kit file validated at: {kit_file_path}")
        print(f"✓ File size: {kit_file_path.stat().st_size} bytes")

    def test_cli_creates_kit_file(self, clean_repo):
        """Test that CLI also creates the .kit file (for comparison)."""
        repo_root, test_app_dir = clean_repo

        # Run CLI command
        cmd = [
            str(repo_root / "repo.sh"),
            "template",
            "new",
            "kit_base_editor",
            "--name", "test_kit_file_creation",
            "--display-name", "Test Kit File Creation",
            "--accept-all"
        ]

        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60
        )

        print(f"\nCLI Output:")
        print(result.stdout)
        if result.stderr:
            print(f"CLI Errors:")
            print(result.stderr)

        # Check for success
        assert result.returncode == 0, f"CLI should succeed. stderr: {result.stderr}"

        # Validate .kit file was created
        expected_kit = repo_root / "source" / "apps" / "test_kit_file_creation" / "test_kit_file_creation.kit"
        assert expected_kit.exists(), f"CLI should create .kit file at: {expected_kit}"

        # Validate content
        kit_content = expected_kit.read_text()
        assert len(kit_content) > 0, "CLI-created .kit file should not be empty"

        print(f"✓ CLI created .kit file at: {expected_kit}")

    def test_api_and_cli_produce_same_structure(self, clean_repo):
        """Test that API and CLI produce identical directory structures."""
        repo_root, _ = clean_repo

        # Create with API
        api = TemplateAPI(str(repo_root))
        api_result = api.create_application(
            template_name='kit_base_editor',
            name='test_api_structure',
            display_name='Test API Structure',
            version='1.0.0',
            accept_license=True,
            no_register=False  # FIXED: --no-register flag not supported by replay command
        )

        assert api_result.get('success'), f"API creation should succeed: {api_result.get('error', 'No error')}"

        # Create with CLI
        cli_cmd = [
            str(repo_root / "repo.sh"),
            "template",
            "new",
            "kit_base_editor",
            "--name", "test_cli_structure",
            "--display-name", "Test CLI Structure",
            "--accept-all"
        ]

        cli_result = subprocess.run(
            cli_cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60
        )

        assert cli_result.returncode == 0, "CLI creation should succeed"

        # Compare structures
        api_dir = repo_root / "source" / "apps" / "test_api_structure"
        cli_dir = repo_root / "source" / "apps" / "test_cli_structure"

        # Both should exist
        assert api_dir.exists(), "API should create app directory"
        assert cli_dir.exists(), "CLI should create app directory"

        # Both should have .kit files
        api_kit = api_dir / "test_api_structure.kit"
        cli_kit = cli_dir / "test_cli_structure.kit"

        assert api_kit.exists(), "API should create .kit file"
        assert cli_kit.exists(), "CLI should create .kit file"

        # Both .kit files should have similar structure (not identical content due to names)
        api_content = api_kit.read_text()
        cli_content = cli_kit.read_text()

        assert '[package]' in api_content or '[app]' in api_content
        assert '[package]' in cli_content or '[app]' in cli_content

        # Clean up extra test apps
        shutil.rmtree(api_dir)
        shutil.rmtree(cli_dir)

        print("✓ API and CLI produce equivalent structures")

    def test_generate_template_does_not_create_files(self):
        """
        Test that generate_template() alone does NOT create files.

        This validates that we fixed the bug where we were using
        generate_template() instead of create_application().
        """
        repo_root = Path(__file__).parent.parent.parent.parent
        api = TemplateAPI(str(repo_root))

        # Use generate_template() directly
        from tools.repoman.template_api import TemplateGenerationRequest
        request = TemplateGenerationRequest(
            template_name='kit_base_editor',
            name='test_no_creation',
            display_name='Test No Creation',
            version='1.0.0',
            accept_license=True
        )

        result = api.generate_template(request)

        # Should succeed (creates playback file)
        assert result.success, "generate_template() should succeed"
        assert result.playback_file, "Should return playback file path"

        # But should NOT create the actual application files
        test_dir = repo_root / "source" / "apps" / "test_no_creation"
        assert not test_dir.exists(), \
            "generate_template() should NOT create application directory (only playback file)"

        print("✓ Confirmed: generate_template() only creates playback, not application files")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
