"""
Unit tests for new TemplateAPI methods.

Tests the execute_playback(), generate_and_execute_template(),
and create_application() methods added in Phase 1.
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.repoman.template_api import (
    TemplateAPI,
    TemplateGenerationRequest,
    TemplateGenerationResult
)


class TestExecutePlayback:
    """Test the execute_playback() method."""

    @patch('subprocess.run')
    def test_execute_playback_success(self, mock_run):
        """Test successful playback execution."""
        # Setup mock
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')

        # Test
        api = TemplateAPI()
        result = api.execute_playback('/path/to/playback.toml')

        # Verify
        assert result.success is True
        assert result.playback_file == '/path/to/playback.toml'
        assert 'successfully' in result.message.lower()

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert 'template' in call_args[0][0]
        assert 'replay' in call_args[0][0]
        assert '/path/to/playback.toml' in call_args[0][0]

    @patch('subprocess.run')
    def test_execute_playback_failure(self, mock_run):
        """Test failed playback execution."""
        # Setup mock
        mock_run.return_value = Mock(
            returncode=1,
            stdout='',
            stderr='Error message'
        )

        # Test
        api = TemplateAPI()
        result = api.execute_playback('/path/to/playback.toml')

        # Verify
        assert result.success is False
        assert result.error is not None
        assert 'failed' in result.error.lower()

    @patch('subprocess.run')
    def test_execute_playback_timeout(self, mock_run):
        """Test playback execution timeout."""
        # Setup mock
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 120)

        # Test
        api = TemplateAPI()
        result = api.execute_playback('/path/to/playback.toml')

        # Verify
        assert result.success is False
        assert result.error is not None
        assert 'timed out' in result.error.lower()

    @patch('subprocess.run')
    def test_execute_playback_with_no_register_flag(self, mock_run):
        """Test that no_register flag is passed correctly."""
        # Setup mock
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')

        # Test
        api = TemplateAPI()
        result = api.execute_playback('/path/to/playback.toml', no_register=True)

        # Verify
        call_args = mock_run.call_args[0][0]
        # The --no-register flag should be in the command
        # (even if not yet implemented in repoman, the API should pass it)
        assert '--no-register' in call_args

    @patch('subprocess.run')
    def test_execute_playback_uses_correct_command(self, mock_run):
        """Test that correct repo command is used based on platform."""
        # Setup mock
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')

        # Test
        api = TemplateAPI()
        result = api.execute_playback('/path/to/playback.toml')

        # Verify command structure
        call_args = mock_run.call_args[0][0]
        assert isinstance(call_args, list)

        # Should have repo.sh or repo.bat
        assert any('repo.' in str(arg) for arg in call_args)

        # Should have template replay
        assert 'template' in call_args
        assert 'replay' in call_args


class TestGenerateAndExecuteTemplate:
    """Test the generate_and_execute_template() method."""

    @patch.object(TemplateAPI, 'execute_playback')
    @patch.object(TemplateAPI, 'generate_template')
    def test_generate_and_execute_success(self, mock_generate, mock_execute):
        """Test successful generation and execution."""
        # Setup mocks
        mock_generate.return_value = TemplateGenerationResult(
            success=True,
            playback_file='/tmp/test.toml',
            message='Generated'
        )
        mock_execute.return_value = TemplateGenerationResult(
            success=True,
            playback_file='/tmp/test.toml',
            message='Executed'
        )

        # Test
        api = TemplateAPI()
        request = TemplateGenerationRequest(
            template_name='test_template',
            name='test_app',
            display_name='Test App',
            version='1.0.0',
            accept_license=True
        )
        result = api.generate_and_execute_template(request)

        # Verify
        assert result.success is True
        assert mock_generate.called
        assert mock_execute.called
        mock_execute.assert_called_with('/tmp/test.toml', False)

    @patch.object(TemplateAPI, 'execute_playback')
    @patch.object(TemplateAPI, 'generate_template')
    def test_generate_and_execute_generation_fails(self, mock_generate, mock_execute):
        """Test when generation fails."""
        # Setup mocks
        mock_generate.return_value = TemplateGenerationResult(
            success=False,
            error='Generation failed'
        )

        # Test
        api = TemplateAPI()
        request = TemplateGenerationRequest(
            template_name='test_template',
            name='test_app',
            display_name='Test App',
            version='1.0.0'
        )
        result = api.generate_and_execute_template(request)

        # Verify
        assert result.success is False
        assert mock_generate.called
        # execute_playback should not be called if generation fails
        assert not mock_execute.called

    @patch.object(TemplateAPI, 'execute_playback')
    @patch.object(TemplateAPI, 'generate_template')
    def test_generate_and_execute_with_no_register(
        self, mock_generate, mock_execute
    ):
        """Test that no_register parameter is passed through."""
        # Setup mocks
        mock_generate.return_value = TemplateGenerationResult(
            success=True,
            playback_file='/tmp/test.toml',
            message='Generated'
        )
        mock_execute.return_value = TemplateGenerationResult(
            success=True,
            playback_file='/tmp/test.toml',
            message='Executed'
        )

        # Test
        api = TemplateAPI()
        request = TemplateGenerationRequest(
            template_name='test_template',
            name='test_app',
            display_name='Test App',
            version='1.0.0'
        )
        result = api.generate_and_execute_template(request, no_register=True)

        # Verify no_register was passed
        mock_execute.assert_called_with('/tmp/test.toml', True)


class TestCreateApplication:
    """Test the create_application() method."""

    @patch.object(TemplateAPI, 'generate_and_execute_template')
    def test_create_application_success(self, mock_generate_execute):
        """Test successful application creation."""
        # Setup mock
        mock_generate_execute.return_value = TemplateGenerationResult(
            success=True,
            playback_file='/tmp/test.toml',
            message='Created'
        )

        # Test
        api = TemplateAPI()
        result = api.create_application(
            template_name='kit_base_editor',
            name='test_app',
            display_name='Test Application',
            version='1.0.0',
            accept_license=True
        )

        # Verify structure
        assert isinstance(result, dict)
        assert result['success'] is True
        assert result['app_name'] == 'test_app'
        assert result['display_name'] == 'Test Application'
        assert 'app_dir' in result
        assert 'kit_file' in result
        assert 'message' in result
        assert 'playback_file' in result

        # Verify paths are strings
        assert isinstance(result['app_dir'], str)
        assert isinstance(result['kit_file'], str)

    @patch.object(TemplateAPI, 'generate_and_execute_template')
    def test_create_application_failure(self, mock_generate_execute):
        """Test failed application creation."""
        # Setup mock
        mock_generate_execute.return_value = TemplateGenerationResult(
            success=False,
            error='Creation failed'
        )

        # Test
        api = TemplateAPI()
        result = api.create_application(
            template_name='kit_base_editor',
            name='test_app',
            display_name='Test Application',
            version='1.0.0'
        )

        # Verify structure
        assert isinstance(result, dict)
        assert result['success'] is False
        assert 'error' in result

    @patch.object(TemplateAPI, 'generate_and_execute_template')
    def test_create_application_passes_parameters(self, mock_generate_execute):
        """Test that parameters are passed correctly."""
        # Setup mock
        mock_generate_execute.return_value = TemplateGenerationResult(
            success=True,
            playback_file='/tmp/test.toml',
            message='Created'
        )

        # Test with extra parameters
        api = TemplateAPI()
        result = api.create_application(
            template_name='kit_base_editor',
            name='test_app',
            display_name='Test Application',
            version='2.0.0',
            accept_license=True,
            no_register=True,
            custom_param='value'
        )

        # Verify method was called
        assert mock_generate_execute.called

        # Get the request that was passed
        call_args = mock_generate_execute.call_args
        request = call_args[0][0]

        # Verify request fields
        assert request.template_name == 'kit_base_editor'
        assert request.name == 'test_app'
        assert request.display_name == 'Test Application'
        assert request.version == '2.0.0'
        assert request.accept_license is True
        assert request.force_overwrite is True  # GUI sets this automatically

        # Verify no_register flag was passed
        no_register_arg = call_args[0][1]
        assert no_register_arg is True

    def test_create_application_return_format(self):
        """Test that return format matches documentation."""
        # This tests the expected interface even if it fails
        api = TemplateAPI()

        # Call with minimal parameters
        result = api.create_application(
            template_name='nonexistent',
            name='test',
            display_name='Test',
            accept_license=False  # Will fail license check
        )

        # Should return dict with success key
        assert isinstance(result, dict)
        assert 'success' in result

        # Failed result should have error
        if not result['success']:
            assert 'error' in result


class TestMethodSignatures:
    """Test that method signatures are correct."""

    def test_execute_playback_signature(self):
        """Test execute_playback has correct signature."""
        import inspect
        sig = inspect.signature(TemplateAPI.execute_playback)

        params = list(sig.parameters.keys())
        assert 'self' in params
        assert 'playback_file' in params
        assert 'no_register' in params

        # no_register should have default value
        assert sig.parameters['no_register'].default is False

    def test_generate_and_execute_template_signature(self):
        """Test generate_and_execute_template has correct signature."""
        import inspect
        sig = inspect.signature(TemplateAPI.generate_and_execute_template)

        params = list(sig.parameters.keys())
        assert 'self' in params
        assert 'request' in params
        assert 'no_register' in params

        # no_register should have default value
        assert sig.parameters['no_register'].default is False

    def test_create_application_signature(self):
        """Test create_application has correct signature."""
        import inspect
        sig = inspect.signature(TemplateAPI.create_application)

        params = list(sig.parameters.keys())
        assert 'self' in params
        assert 'template_name' in params
        assert 'name' in params
        assert 'display_name' in params
        assert 'version' in params
        assert 'accept_license' in params
        assert 'no_register' in params
        assert 'kwargs' in params  # For extra parameters

        # Check defaults
        assert sig.parameters['version'].default == "0.1.0"
        assert sig.parameters['accept_license'].default is False
        assert sig.parameters['no_register'].default is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
