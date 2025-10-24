#!/usr/bin/env python3
"""
API Documentation Routes.

Provides OpenAPI specification and Swagger UI for API documentation.
"""

from flask import Blueprint, jsonify, render_template_string
import logging

from kit_playground.backend.openapi_spec import get_openapi_spec

logger = logging.getLogger(__name__)


def create_docs_routes() -> Blueprint:
    """Create and configure documentation routes."""
    
    docs_bp = Blueprint('docs', __name__, url_prefix='/api')
    
    @docs_bp.route('/openapi.json', methods=['GET'])
    def get_openapi():
        """
        Get OpenAPI 3.0 specification in JSON format.
        
        Returns the complete API specification that can be used with
        Swagger UI, Postman, or other OpenAPI-compatible tools.
        """
        try:
            spec = get_openapi_spec()
            return jsonify(spec)
        except Exception as e:
            logger.error(f"Error generating OpenAPI spec: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @docs_bp.route('/docs', methods=['GET'])
    def swagger_ui():
        """
        Serve Swagger UI for interactive API documentation.
        
        Provides an interactive interface to explore and test API endpoints.
        """
        # Embedded Swagger UI HTML
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kit Playground API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.3/swagger-ui.css">
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin: 0; padding: 0; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.3/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.3/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/api/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
            window.ui = ui;
        };
    </script>
</body>
</html>
        """
        return render_template_string(html)
    
    return docs_bp

