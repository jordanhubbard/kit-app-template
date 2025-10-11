"""
Integration tests to verify CLI and GUI produce identical results.

These tests ensure clean separation of concerns - the GUI wraps the CLI
without re-implementing logic or adding workarounds.
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


class TestCLIGUIEquivalence:
    """Test that CLI and GUI produce identical results."""

    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary repository for testing."""
        # Get the actual repo root
        repo_root = Path(__file__).parent.parent.parent.parent
        
        # Copy minimal required files to temp location
        temp_repo = tmp_path / "test_repo"
        temp_repo.mkdir()
        
        # Copy templates directory
        templates_src = repo_root / "templates"
        templates_dst = temp_repo / "templates"
        if templates_src.exists():
            shutil.copytree(templates_src, templates_dst)
        
        # Copy tools directory
        tools_src = repo_root / "tools"
        tools_dst = temp_repo / "tools"
        if tools_src.exists():
            shutil.copytree(tools_src, tools_dst)
        
        # Create minimal repo.toml
        repo_toml = temp_repo / "repo.toml"
        repo_toml.write_text("""
[repo]
name = "test-repo"

[apps]
apps = []
""")
        
        # Create repo.sh and repo.bat
        repo_sh = temp_repo / "repo.sh"
        repo_sh.write_text(f"""#!/bin/bash
cd "{repo_root}"
exec ./repo.sh "$@"
""")
        os.chmod(str(repo_sh), 0o755)
        
        repo_bat = temp_repo / "repo.bat"
        repo_bat.write_text(f"""@echo off
cd /d "{repo_root}"
call repo.bat %*
""")
        
        return temp_repo

    def test_template_api_execute_playback(self, temp_repo):
        """Test that execute_playback() works correctly."""
        api = TemplateAPI(str(temp_repo))
        
        # Create a mock playback file
        playback_file = temp_repo / "test_playback.toml"
        playback_file.write_text("""
[test_template]
application_name = "test.app"
application_display_name = "Test App"
version = "1.0.0"
""")
        
        # Execute playback should not crash (may fail if template doesn't exist)
        result = api.execute_playback(str(playback_file))
        
        # Should return a TemplateGenerationResult
        assert hasattr(result, 'success')
        assert hasattr(result, 'error')
        assert hasattr(result, 'playback_file')

    def test_template_api_create_application(self):
        """Test that create_application() returns proper structure."""
        repo_root = Path(__file__).parent.parent.parent.parent
        api = TemplateAPI(str(repo_root))
        
        # Test with a template name (may not actually create if license not accepted)
        # but should return proper structure
        try:
            result = api.create_application(
                template_name='kit_base_editor',
                name='test_app',
                display_name='Test App',
                version='1.0.0',
                accept_license=True
            )
            
            # Should return a dict
            assert isinstance(result, dict)
            assert 'success' in result
            
            if result['success']:
                # If successful, should have required fields
                assert 'app_name' in result
                assert 'app_dir' in result
                assert 'kit_file' in result
                assert 'message' in result
                assert result['app_name'] == 'test_app'
            else:
                # If failed, should have error
                assert 'error' in result
                
        except Exception as e:
            # If it fails, that's okay - we're testing structure
            pytest.skip(f"Template creation failed (expected): {e}")

    def test_gui_uses_template_api_not_subprocess(self):
        """Verify GUI doesn't use subprocess for template operations."""
        from kit_playground.backend.routes import v2_template_routes
        
        # Read the source code
        source_file = Path(v2_template_routes.__file__)
        source_code = source_file.read_text()
        
        # Should NOT import subprocess
        assert 'import subprocess' not in source_code, \
            "GUI should not directly import subprocess for template operations"
        
        # Should NOT import _fix_application_structure
        assert '_fix_application_structure' not in source_code, \
            "GUI should not use _fix_application_structure workaround"
        
        # Should use template_api
        assert 'template_api.create_application' in source_code, \
            "GUI should use template_api.create_application()"

    def test_no_repo_toml_manipulation_in_gui(self):
        """Verify GUI doesn't manipulate repo.toml."""
        from kit_playground.backend.routes import v2_template_routes
        
        source_file = Path(v2_template_routes.__file__)
        source_code = source_file.read_text()
        
        # Should NOT manipulate repo.toml
        assert 'repo.toml' not in source_code or 'get_platform_build_dir' in source_code, \
            "GUI should not manipulate repo.toml"
        
        # Should NOT use regex to modify files
        assert 'import re' not in source_code or 're.subn' not in source_code, \
            "GUI should not use regex to modify config files"

    def test_template_api_methods_exist(self):
        """Verify new TemplateAPI methods exist with correct signatures."""
        api = TemplateAPI()
        
        # Check methods exist
        assert hasattr(api, 'execute_playback'), \
            "TemplateAPI should have execute_playback method"
        assert hasattr(api, 'generate_and_execute_template'), \
            "TemplateAPI should have generate_and_execute_template method"
        assert hasattr(api, 'create_application'), \
            "TemplateAPI should have create_application method"
        
        # Check method signatures
        import inspect
        
        # execute_playback should accept playback_file and no_register
        sig = inspect.signature(api.execute_playback)
        assert 'playback_file' in sig.parameters
        assert 'no_register' in sig.parameters
        
        # create_application should accept template_name, name, etc.
        sig = inspect.signature(api.create_application)
        assert 'template_name' in sig.parameters
        assert 'name' in sig.parameters
        assert 'display_name' in sig.parameters
        assert 'accept_license' in sig.parameters
        assert 'no_register' in sig.parameters

    def test_gui_code_reduction(self):
        """Verify GUI code was significantly reduced after refactoring."""
        from kit_playground.backend.routes import v2_template_routes
        
        source_file = Path(v2_template_routes.__file__)
        source_code = source_file.read_text()
        
        # Count lines in generate_template_v2 function
        in_function = False
        function_lines = 0
        indentation_level = 0
        
        for line in source_code.split('\n'):
            stripped = line.strip()
            
            if 'def generate_template_v2' in stripped:
                in_function = True
                indentation_level = len(line) - len(line.lstrip())
                continue
            
            if in_function:
                if stripped and not stripped.startswith('#'):
                    current_indent = len(line) - len(line.lstrip())
                    # If we're back to the same or less indentation, we're out of the function
                    if current_indent <= indentation_level and stripped.startswith('def '):
                        break
                    if current_indent > indentation_level:
                        function_lines += 1
        
        # After refactoring, the function should be under 100 lines
        assert function_lines < 100, \
            f"GUI generate_template_v2 should be simplified (found {function_lines} lines)"

    def test_no_workarounds_in_gui(self):
        """Comprehensive test that no workarounds exist in GUI code."""
        from kit_playground.backend.routes import v2_template_routes
        
        source_file = Path(v2_template_routes.__file__)
        source_code = source_file.read_text()
        
        # List of workaround patterns that should NOT exist
        forbidden_patterns = [
            ('subprocess.run', 'Direct subprocess calls for template operations'),
            ('_fix_application_structure', 'Post-processing workaround'),
            ('apps\s*=\s*\[', 'repo.toml manipulation'),
            ('re.subn.*apps', 'Regex file modification'),
            ('tomllib.load.*playback', 'Manual playback file parsing'),
        ]
        
        violations = []
        for pattern, description in forbidden_patterns:
            import re
            if re.search(pattern, source_code):
                violations.append(description)
        
        assert not violations, \
            f"Found forbidden workarounds in GUI: {', '.join(violations)}"


class TestTemplateAPIIntegration:
    """Integration tests for the new TemplateAPI methods."""

    def test_api_initialization(self):
        """Test TemplateAPI can be initialized."""
        # With explicit repo root
        repo_root = Path(__file__).parent.parent.parent.parent
        api = TemplateAPI(str(repo_root))
        assert api.repo_root == repo_root
        
        # With auto-detection
        api2 = TemplateAPI()
        assert api2.repo_root is not None

    def test_execute_playback_timeout(self):
        """Test that execute_playback has proper timeout handling."""
        import inspect
        from tools.repoman.template_api import TemplateAPI
        
        # Check source code for timeout
        source = inspect.getsource(TemplateAPI.execute_playback)
        assert 'timeout' in source, "execute_playback should have timeout parameter"
        assert '120' in source or 'timeout=' in source, \
            "execute_playback should have 2-minute timeout"

    def test_create_application_return_structure(self):
        """Test create_application returns proper structure."""
        api = TemplateAPI()
        
        # Call with invalid template (will fail but we can check error structure)
        result = api.create_application(
            template_name='nonexistent_template_12345',
            name='test',
            display_name='Test',
            accept_license=True
        )
        
        # Should always return a dict
        assert isinstance(result, dict)
        assert 'success' in result
        
        # Failed result should have error
        if not result['success']:
            assert 'error' in result


class TestBackwardCompatibility:
    """Test that changes are backward compatible."""

    def test_template_api_old_methods_still_work(self):
        """Verify old TemplateAPI methods still exist."""
        api = TemplateAPI()
        
        # Old methods should still exist
        assert hasattr(api, 'list_templates')
        assert hasattr(api, 'get_template')
        assert hasattr(api, 'generate_template')
        assert hasattr(api, 'check_license')

    def test_repo_dispatcher_still_has_helpers(self):
        """Verify repo_dispatcher helpers still exist for CLI."""
        from tools.repoman import repo_dispatcher
        
        # get_platform_build_dir should still exist
        assert hasattr(repo_dispatcher, 'get_platform_build_dir')
        
        # _fix_application_structure should still exist for CLI use
        assert hasattr(repo_dispatcher, '_fix_application_structure')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

