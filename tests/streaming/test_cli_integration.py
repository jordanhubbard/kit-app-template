#!/usr/bin/env python3
"""
CLI Integration tests for Kit App Streaming.

Tests the command-line integration to ensure streaming flags
are properly recognized and processed.
"""

import subprocess
import sys
from pathlib import Path

import pytest


repo_root = Path(__file__).parent.parent.parent


class TestCLIFlags:
    """Test CLI flag recognition."""

    def test_help_shows_streaming_flags(self):
        """Verify --streaming flag appears in help."""
        result = subprocess.run(
            ["./repo.sh", "launch", "--help"],
            capture_output=True,
            text=True,
            cwd=repo_root
        )

        # Should mention streaming in help
        output = result.stdout + result.stderr
        assert "--streaming" in output
        assert "--streaming-port" in output

    def test_streaming_flag_syntax(self):
        """Verify streaming flag doesn't cause parse errors."""
        # This should parse without error (even if no app specified)
        result = subprocess.run(
            ["./repo.sh", "launch", "--streaming", "--help"],
            capture_output=True,
            text=True,
            cwd=repo_root
        )

        # Should not have syntax errors
        assert result.returncode in [0, 2]  # 0 or help exit code
        assert "unrecognized arguments" not in result.stderr.lower()

    def test_streaming_port_flag_syntax(self):
        """Verify streaming-port flag accepts numeric value."""
        result = subprocess.run(
            ["./repo.sh", "launch", "--streaming-port", "48000", "--help"],
            capture_output=True,
            text=True,
            cwd=repo_root
        )

        # Should not have syntax errors
        assert result.returncode in [0, 2]
        assert "unrecognized arguments" not in result.stderr.lower()


class TestStreamingTemplates:
    """Test against actual streaming templates if available."""

    def test_streaming_templates_exist(self):
        """Check if streaming templates are available."""
        templates_dir = repo_root / "templates" / "apps" / "streaming_configs"

        if templates_dir.exists():
            streaming_files = list(templates_dir.glob("*.kit"))
            print(f"\nFound {len(streaming_files)} streaming template(s):")
            for f in streaming_files:
                print(f"  - {f.name}")

            # At minimum, we should have templates defined
            assert len(streaming_files) > 0, "No streaming templates found"
        else:
            pytest.skip("Streaming templates directory not found")

    def test_template_list_command(self):
        """Verify template list command works."""
        result = subprocess.run(
            ["./repo.sh", "template", "list"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=30
        )

        # Should execute without error
        assert result.returncode == 0

        # Should list templates
        output = result.stdout + result.stderr
        # May or may not have streaming templates visible in list
        # depending on template registry configuration


class TestLaunchIntegration:
    """Test launch.py integration."""

    def test_launch_module_imports(self):
        """Verify launch.py can be imported."""
        launch_py = repo_root / "tools" / "repoman" / "launch.py"
        assert launch_py.exists()

        # Try importing (syntax check)
        sys.path.insert(0, str(repo_root / "tools" / "repoman"))
        try:
            import launch
            # Verify our new functions exist
            assert hasattr(launch, 'launch_kit')
            assert hasattr(launch, 'add_args')
        except Exception as e:
            pytest.fail(f"Failed to import launch.py: {e}")

    def test_streaming_utils_import_from_launch(self):
        """Verify streaming_utils can be imported by launch.py."""
        sys.path.insert(0, str(repo_root / "tools" / "repoman"))

        try:
            from streaming_utils import is_streaming_app
            # If this succeeds, launch.py can import it too
            assert callable(is_streaming_app)
        except ImportError as e:
            pytest.fail(f"streaming_utils not importable: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
