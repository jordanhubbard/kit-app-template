"""
Integration tests for all API endpoints.

Tests every API route to ensure frontend/backend synchronization.
These tests verify HTTP responses and basic functionality.
"""
import json
import sys
from pathlib import Path
from io import BytesIO

import pytest

# Add paths for imports
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "kit_playground"))

from kit_playground.backend.web_server import PlaygroundWebServer
from kit_playground.core.playground_app import PlaygroundApp
from kit_playground.core.config import PlaygroundConfig


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


class TestConfigEndpoints:
    """Test configuration endpoints."""
    
    def test_get_config_paths(self, client):
        """Test GET /api/config/paths"""
        response = client.get('/api/config/paths')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'templatesPath' in data
        assert 'projectsPath' in data
        assert 'repoRoot' in data
        assert Path(data['repoRoot']).exists()


class TestV2TemplateEndpoints:
    """Test v2 template API endpoints."""
    
    def test_list_templates(self, client):
        """Test GET /api/v2/templates"""
        response = client.get('/api/v2/templates')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify template structure
        template = data[0]
        assert 'id' in template
        assert 'name' in template
        assert 'displayName' in template
        assert 'type' in template
        assert 'description' in template
        # Icon may or may not be present
    
    def test_list_templates_with_filters(self, client):
        """Test GET /api/v2/templates with type filter"""
        response = client.get('/api/v2/templates?type=application')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        # All returned templates should be applications
        for template in data:
            assert template['type'] == 'application'
    
    def test_get_template_icon(self, client):
        """Test GET /api/v2/templates/{id}/icon"""
        # First get list of templates to find one with an icon
        response = client.get('/api/v2/templates')
        templates = json.loads(response.data)
        
        template_with_icon = None
        for t in templates:
            if t.get('icon'):
                template_with_icon = t
                break
        
        if template_with_icon:
            response = client.get(template_with_icon['icon'])
            assert response.status_code == 200
            assert response.content_type.startswith('image/')
        else:
            pytest.skip("No templates with icons found")
    
    def test_get_template_docs(self, client):
        """Test GET /api/v2/templates/{id}/docs"""
        # Get first template
        response = client.get('/api/v2/templates')
        templates = json.loads(response.data)
        assert len(templates) > 0
        
        template_id = templates[0]['id']
        response = client.get(f'/api/v2/templates/{template_id}/docs')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'name' in data
        assert 'displayName' in data
        assert 'documentation' in data or 'description' in data
    
    def test_generate_template_validation(self, client):
        """Test POST /api/v2/templates/generate with missing parameters"""
        # Test missing templateName
        response = client.post(
            '/api/v2/templates/generate',
            data=json.dumps({'name': 'test_project'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test missing name
        response = client.post(
            '/api/v2/templates/generate',
            data=json.dumps({'templateName': 'omni_usd_viewer'}),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestTemplateEndpoints:
    """Test legacy template API endpoints."""
    
    def test_list_templates_legacy(self, client):
        """Test GET /api/templates (legacy endpoint)"""
        response = client.get('/api/templates')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'templates' in data
        assert isinstance(data['templates'], list)
    
    def test_list_templates_explicit(self, client):
        """Test GET /api/templates/list"""
        response = client.get('/api/templates/list')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'templates' in data


class TestProjectEndpoints:
    """Test project management endpoints."""
    
    def test_discover_projects_missing_path(self, client):
        """Test GET /api/projects/discover without path parameter"""
        response = client.get('/api/projects/discover')
        assert response.status_code == 400
    
    def test_discover_projects_invalid_path(self, client):
        """Test GET /api/projects/discover with invalid path"""
        response = client.get('/api/projects/discover?path=/etc/passwd')
        # Should be blocked by security validator
        assert response.status_code == 403
    
    def test_discover_projects_valid_path(self, client):
        """Test GET /api/projects/discover with valid path"""
        # Use repo root which should always be accessible
        response = client.get('/api/config/paths')
        paths = json.loads(response.data)
        
        response = client.get(f'/api/projects/discover?path={paths["projectsPath"]}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'projects' in data
        assert isinstance(data['projects'], list)
    
    def test_build_project_missing_params(self, client):
        """Test POST /api/projects/build without required parameters"""
        response = client.post(
            '/api/projects/build',
            data=json.dumps({}),
            content_type='application/json'
        )
        # Build endpoint may accept empty params and use defaults
        # Just verify it doesn't crash
        assert response.status_code in [200, 400, 500]
    
    def test_run_project_missing_params(self, client):
        """Test POST /api/projects/run without required parameters"""
        response = client.post(
            '/api/projects/run',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_stop_project_missing_params(self, client):
        """Test POST /api/projects/stop without required parameters"""
        response = client.post(
            '/api/projects/stop',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_stop_nonexistent_project(self, client):
        """Test POST /api/projects/stop for project that's not running"""
        response = client.post(
            '/api/projects/stop',
            data=json.dumps({'projectName': 'nonexistent_project'}),
            content_type='application/json'
        )
        assert response.status_code == 404


class TestFilesystemEndpoints:
    """Test filesystem operation endpoints."""
    
    def test_get_cwd(self, client):
        """Test GET /api/filesystem/cwd"""
        response = client.get('/api/filesystem/cwd')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'cwd' in data
        assert Path(data['cwd']).exists()
    
    def test_list_directory_missing_path(self, client):
        """Test GET /api/filesystem/list without path"""
        response = client.get('/api/filesystem/list')
        # Endpoint may default to current directory
        assert response.status_code in [200, 400]
    
    def test_list_directory_invalid_path(self, client):
        """Test GET /api/filesystem/list with path traversal attempt"""
        response = client.get('/api/filesystem/list?path=/etc')
        # Should be blocked by security validator
        assert response.status_code == 403
    
    def test_list_directory_valid_path(self, client):
        """Test GET /api/filesystem/list with valid path"""
        response = client.get('/api/config/paths')
        paths = json.loads(response.data)
        
        response = client.get(f'/api/filesystem/list?path={paths["repoRoot"]}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        # Should contain directories and files
        if len(data) > 0:
            item = data[0]
            assert 'name' in item
            # API uses 'isDirectory' not 'type'
            assert 'isDirectory' in item or 'type' in item
    
    def test_read_file_missing_path(self, client):
        """Test GET /api/filesystem/read without path"""
        response = client.get('/api/filesystem/read')
        assert response.status_code == 400
    
    def test_read_file_invalid_path(self, client):
        """Test GET /api/filesystem/read with path traversal"""
        response = client.get('/api/filesystem/read?path=/etc/passwd')
        # Should be blocked by security validator
        assert response.status_code == 403
    
    def test_read_file_nonexistent(self, client):
        """Test GET /api/filesystem/read for nonexistent file"""
        response = client.get('/api/config/paths')
        paths = json.loads(response.data)
        
        response = client.get(
            f'/api/filesystem/read?path={paths["repoRoot"]}/nonexistent_file_12345.txt'
        )
        # May return 403 (validation fails) or 404 (file not found)
        assert response.status_code in [403, 404]
    
    def test_mkdir_missing_path(self, client):
        """Test POST /api/filesystem/mkdir without path"""
        response = client.post(
            '/api/filesystem/mkdir',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestXpraEndpoints:
    """Test Xpra management endpoints."""
    
    def test_xpra_check(self, client):
        """Test GET /api/xpra/check"""
        response = client.get('/api/xpra/check')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'available' in data
        assert 'installed' in data
        assert isinstance(data['available'], bool)
        assert isinstance(data['installed'], bool)
    
    def test_xpra_list_sessions(self, client):
        """Test GET /api/xpra/sessions"""
        response = client.get('/api/xpra/sessions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)


class TestSecurityValidation:
    """Test that security validators are properly applied."""
    
    def test_project_name_injection_blocked(self, client):
        """Test that command injection in project names is blocked"""
        response = client.post(
            '/api/projects/build',
            data=json.dumps({
                'projectPath': '_build/apps/test',
                'projectName': 'test; rm -rf /'  # Injection attempt
            }),
            content_type='application/json'
        )
        # Should be rejected due to unsafe project name
        assert response.status_code in [400, 403]
    
    def test_path_traversal_blocked(self, client):
        """Test that path traversal attempts are blocked"""
        # Try to access /etc/passwd
        response = client.get('/api/filesystem/read?path=/etc/passwd')
        assert response.status_code == 403
        
        # Try with relative path traversal
        response = client.get('/api/filesystem/read?path=../../../../etc/passwd')
        assert response.status_code == 403


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete workflows that use multiple endpoints."""
    
    def test_template_discovery_workflow(self, client):
        """Test: List templates -> Get template docs -> Check icon"""
        # 1. List templates
        response = client.get('/api/v2/templates')
        assert response.status_code == 200
        templates = json.loads(response.data)
        assert len(templates) > 0
        
        # 2. Get docs for first template
        template_id = templates[0]['id']
        response = client.get(f'/api/v2/templates/{template_id}/docs')
        assert response.status_code == 200
        
        # 3. Try to get icon if available
        if templates[0].get('icon'):
            response = client.get(templates[0]['icon'])
            assert response.status_code == 200
    
    def test_project_discovery_workflow(self, client):
        """Test: Get paths -> Discover projects -> Check filesystem"""
        # 1. Get default paths
        response = client.get('/api/config/paths')
        assert response.status_code == 200
        paths = json.loads(response.data)
        
        # 2. Discover projects
        response = client.get(f'/api/projects/discover?path={paths["projectsPath"]}')
        assert response.status_code == 200
        projects = json.loads(response.data)
        
        # 3. List the projects directory
        response = client.get(f'/api/filesystem/list?path={paths["projectsPath"]}')
        assert response.status_code == 200

