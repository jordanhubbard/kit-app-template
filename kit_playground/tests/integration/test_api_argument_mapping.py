"""
Integration tests for API argument mapping and validation.

Ensures that arguments passed from UI -> Backend Routes -> Template API
are correctly mapped and validated at each layer.
"""
import json
import sys
from pathlib import Path

import pytest

# Add paths for imports
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "kit_playground"))

from kit_playground.backend.web_server import PlaygroundWebServer
from kit_playground.core.playground_app import PlaygroundApp
from kit_playground.core.config import PlaygroundConfig
from tools.repoman.template_api import TemplateGenerationRequest


@pytest.fixture(scope="module")
def app():
    """Create a Flask app for testing."""
    config = PlaygroundConfig()
    playground_app = PlaygroundApp(config)
    server = PlaygroundWebServer(playground_app, config)
    server.app.config['TESTING'] = True
    return server.app


@pytest.fixture(scope="module")
def client(app):
    """Create a test client."""
    return app.test_client()


class TestTemplateGenerationArgumentMapping:
    """Test that template generation arguments are correctly mapped through all layers."""
    
    def test_template_generation_request_structure(self):
        """Verify TemplateGenerationRequest has the expected fields."""
        import dataclasses
        
        fields = {f.name for f in dataclasses.fields(TemplateGenerationRequest)}
        
        # These are the required fields that must be present
        required_fields = {
            'template_name',
            'name',
            'display_name',
            'version',
            'output_dir',
            'accept_license',
            'extra_params'
        }
        
        assert required_fields.issubset(fields), \
            f"Missing required fields in TemplateGenerationRequest: {required_fields - fields}"
    
    def test_v2_generate_endpoint_argument_mapping(self, client):
        """Test that /api/v2/templates/generate correctly maps arguments."""
        # This should fail because we're not creating a real project,
        # but it should fail AFTER argument mapping succeeds
        response = client.post(
            '/api/v2/templates/generate',
            data=json.dumps({
                'templateName': 'omni_usd_viewer',
                'name': 'test_argument_mapping',
                'displayName': 'Test Argument Mapping',
                'version': '1.0.0',
                'outputDir': '_build/test_temp',
                'options': {'test_option': 'test_value'}
            }),
            content_type='application/json'
        )
        
        # Should not return 500 due to attribute error
        # May fail with other errors (like missing dependencies) but not AttributeError
        data = json.loads(response.data)
        
        if not data.get('success'):
            # If it failed, make sure it's not due to wrong attribute names
            error = data.get('error', '')
            assert 'attribute' not in error.lower(), \
                f"Attribute error suggests wrong parameter mapping: {error}"
            assert 'generate' not in error or 'generate_template' in error, \
                f"Method name error: {error}"
    
    def test_legacy_create_endpoint_argument_mapping(self, client):
        """Test that /api/templates/create correctly maps arguments."""
        response = client.post(
            '/api/templates/create',
            data=json.dumps({
                'template': 'omni_usd_viewer',
                'name': 'test_legacy_mapping',
                'displayName': 'Test Legacy Mapping',
                'version': '1.0.0',
                'outputDir': '_build/test_temp',
                'options': {}
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        if not data.get('success'):
            error = data.get('error', '')
            # Same checks - should not fail due to attribute/parameter errors
            assert 'attribute' not in error.lower(), \
                f"Attribute error in legacy endpoint: {error}"
            assert 'unexpected keyword' not in error.lower(), \
                f"Parameter mapping error: {error}"


class TestProjectBuildRunArgumentMapping:
    """Test project build/run argument mapping."""
    
    def test_build_endpoint_accepts_correct_parameters(self, client):
        """Test that /api/projects/build accepts the correct parameters."""
        response = client.post(
            '/api/projects/build',
            data=json.dumps({
                'projectPath': '_build/apps/nonexistent',
                'projectName': 'test_project',
                'config': 'release'
            }),
            content_type='application/json'
        )
        
        # Should not crash with parameter errors
        # May fail for other reasons (project doesn't exist, etc.)
        assert response.status_code in [200, 400, 403, 404, 500]
        data = json.loads(response.data)
        
        if 'error' in data:
            error = data['error']
            # Should not be a Python argument error
            assert 'unexpected keyword' not in error.lower()
            assert 'missing.*required.*argument' not in error.lower()
    
    def test_run_endpoint_accepts_correct_parameters(self, client):
        """Test that /api/projects/run accepts the correct parameters."""
        response = client.post(
            '/api/projects/run',
            data=json.dumps({
                'projectPath': '_build/apps/nonexistent',
                'projectName': 'test_project',
                'useXpra': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 403, 404, 500]
        data = json.loads(response.data)
        
        if 'error' in data:
            error = data['error']
            assert 'unexpected keyword' not in error.lower()
            assert 'missing.*required.*argument' not in error.lower()
    
    def test_stop_endpoint_accepts_correct_parameters(self, client):
        """Test that /api/projects/stop accepts projectName in body."""
        response = client.post(
            '/api/projects/stop',
            data=json.dumps({
                'projectName': 'nonexistent_project'
            }),
            content_type='application/json'
        )
        
        # Should return 404 (not running) not 400 (bad parameters)
        assert response.status_code in [404, 500]


class TestFilesystemArgumentMapping:
    """Test filesystem endpoint argument mapping."""
    
    def test_list_accepts_path_parameter(self, client):
        """Test that /api/filesystem/list accepts path query parameter."""
        # Get a valid path first
        config_response = client.get('/api/config/paths')
        paths = json.loads(config_response.data)
        
        response = client.get(f'/api/filesystem/list?path={paths["repoRoot"]}')
        
        # Should succeed
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_read_accepts_path_parameter(self, client):
        """Test that /api/filesystem/read accepts path query parameter."""
        # Try to read the repo.toml file
        config_response = client.get('/api/config/paths')
        paths = json.loads(config_response.data)
        
        test_file = f"{paths['repoRoot']}/repo.toml"
        response = client.get(f'/api/filesystem/read?path={test_file}')
        
        # Should succeed or return 403/404, not parameter error
        assert response.status_code in [200, 403, 404]
    
    def test_mkdir_accepts_path_in_body(self, client):
        """Test that /api/filesystem/mkdir accepts path in request body."""
        response = client.post(
            '/api/filesystem/mkdir',
            data=json.dumps({
                'path': '/tmp/test_mkdir_argument_test_12345'
            }),
            content_type='application/json'
        )
        
        # Should succeed or fail validation, not parameter error
        assert response.status_code in [200, 400, 403]


class TestDiscoverArgumentMapping:
    """Test project discovery argument mapping."""
    
    def test_discover_requires_path_parameter(self, client):
        """Test that /api/projects/discover requires path parameter."""
        # Without path - should return 400
        response = client.get('/api/projects/discover')
        assert response.status_code == 400
        
        # With path - should work
        config_response = client.get('/api/config/paths')
        paths = json.loads(config_response.data)
        
        response = client.get(f'/api/projects/discover?path={paths["projectsPath"]}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'projects' in data


class TestCrossLayerValidation:
    """Test that data flows correctly through all layers."""
    
    def test_ui_to_backend_to_api_data_flow(self, client):
        """
        Simulate the full data flow:
        UI (TypeScript) -> Backend Routes (Flask) -> Template API (Python)
        """
        # This mimics what the UI sends
        ui_payload = {
            'templateName': 'base_application',  # UI uses camelCase
            'name': 'test.flow.validation',
            'displayName': 'Test Flow Validation',
            'version': '0.1.0',
            'outputDir': '_build/test_flow',
            'options': {
                'customOption': 'customValue'
            }
        }
        
        response = client.post(
            '/api/v2/templates/generate',
            data=json.dumps(ui_payload),
            content_type='application/json'
        )
        
        # Check response structure
        data = json.loads(response.data)
        
        # Even if generation fails, the structure should be correct
        assert 'success' in data
        
        if data['success']:
            # If successful, check return structure matches UI expectations
            assert 'projectInfo' in data
            project_info = data['projectInfo']
            assert 'projectName' in project_info
            assert 'displayName' in project_info
            assert 'outputDir' in project_info
            assert 'kitFile' in project_info
        else:
            # If failed, should have error message
            assert 'error' in data
            error = data['error']
            
            # Should NOT be parameter/attribute errors
            assert 'has no attribute' not in error
            assert 'unexpected keyword argument' not in error
            assert 'missing.*required.*positional argument' not in error.lower()

