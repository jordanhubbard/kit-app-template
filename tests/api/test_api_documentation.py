#!/usr/bin/env python3
"""
API Documentation Tests.

Tests for OpenAPI/Swagger documentation endpoints.
"""

import pytest
import json


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_spec_endpoint(self, api_client):
        """Verify OpenAPI spec endpoint returns JSON."""
        response = api_client.get('/api/openapi.json')

        assert response.status_code == 200
        assert response.is_json

        spec = response.get_json()
        assert 'openapi' in spec
        assert spec['openapi'] == '3.0.0'
        print(f"✅ OpenAPI spec version: {spec['openapi']}")

    def test_openapi_spec_structure(self, api_client):
        """Verify OpenAPI spec has required fields."""
        response = api_client.get('/api/openapi.json')
        spec = response.get_json()

        # Check required top-level fields
        assert 'info' in spec
        assert 'paths' in spec
        assert 'components' in spec

        # Check info section
        assert 'title' in spec['info']
        assert 'version' in spec['info']
        assert spec['info']['title'] == 'Kit Playground API'

        print(f"✅ API title: {spec['info']['title']}")

    def test_openapi_has_template_endpoints(self, api_client):
        """Verify template endpoints are documented."""
        response = api_client.get('/api/openapi.json')
        spec = response.get_json()

        paths = spec.get('paths', {})

        # Check for key endpoints
        assert '/api/templates/list' in paths
        assert '/api/templates/get/{name}' in paths
        assert '/api/templates/create' in paths

        print(f"✅ Template endpoints documented: {len([p for p in paths if 'template' in p])}")

    def test_openapi_has_job_endpoints(self, api_client):
        """Verify job management endpoints are documented."""
        response = api_client.get('/api/openapi.json')
        spec = response.get_json()

        paths = spec.get('paths', {})

        # Check for job endpoints
        assert '/api/jobs' in paths
        assert '/api/jobs/{job_id}' in paths
        assert '/api/jobs/{job_id}/cancel' in paths
        assert '/api/jobs/{job_id}/logs' in paths
        assert '/api/jobs/stats' in paths

        print(f"✅ Job endpoints documented: {len([p for p in paths if 'job' in p])}")

    def test_openapi_has_schemas(self, api_client):
        """Verify schemas are defined."""
        response = api_client.get('/api/openapi.json')
        spec = response.get_json()

        schemas = spec.get('components', {}).get('schemas', {})

        # Check for key schemas
        assert 'Template' in schemas
        assert 'Job' in schemas
        assert 'Error' in schemas

        print(f"✅ Schemas defined: {len(schemas)}")

    def test_swagger_ui_endpoint(self, api_client):
        """Verify Swagger UI endpoint returns HTML."""
        response = api_client.get('/api/docs')

        assert response.status_code == 200
        assert response.content_type.startswith('text/html')

        # Check for Swagger UI elements in HTML
        html = response.get_data(as_text=True)
        assert 'swagger-ui' in html.lower()
        assert 'openapi.json' in html

        print(f"✅ Swagger UI endpoint serves HTML ({len(html)} bytes)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
