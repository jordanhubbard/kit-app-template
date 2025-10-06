"""
Template management routes for Kit Playground.
"""
import logging
from pathlib import Path
from flask import Blueprint, jsonify, request

from tools.repoman.template_api import TemplateAPI, TemplateGenerationRequest
from tools.repoman.template_engine import TemplateEngine

logger = logging.getLogger(__name__)

# Create blueprint
template_bp = Blueprint('templates', __name__, url_prefix='/api/templates')


def create_template_routes(playground_app, template_api: TemplateAPI):
    """
    Create and configure template routes.
    
    Args:
        playground_app: PlaygroundApp instance
        template_api: TemplateAPI instance for template operations
    
    Returns:
        Flask Blueprint with template routes configured
    """
    
    @template_bp.route('/list', methods=['GET'])
    def list_templates():
        """List all available templates."""
        try:
            templates = template_api.list_templates()
            return jsonify({'templates': templates})
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return jsonify({'error': str(e)}), 500

    @template_bp.route('/get/<template_name>', methods=['GET'])
    def get_template(template_name: str):
        """Get details of a specific template."""
        try:
            template = template_api.get_template(template_name)
            if template is None:
                return jsonify({'error': f'Template {template_name} not found'}), 404
            return jsonify({'template': template})
        except Exception as e:
            logger.error(f"Failed to get template {template_name}: {e}")
            return jsonify({'error': str(e)}), 500

    @template_bp.route('/create', methods=['POST'])
    def create_from_template():
        """Create a new project from a template."""
        try:
            data = request.json
            template_name = data.get('template')
            project_name = data.get('name')
            display_name = data.get('displayName', project_name)
            output_dir = data.get('outputDir', '_build/apps')

            if not template_name or not project_name:
                return jsonify({
                    'error': 'template and name are required'
                }), 400

            # Prepare generation request
            gen_request = TemplateGenerationRequest(
                template_name=template_name,
                project_name=project_name,
                display_name=display_name,
                version=data.get('version', '1.0.0'),
                output_directory=output_dir,
                options=data.get('options', {})
            )

            # Generate project
            result = template_api.generate(gen_request)

            if result.success:
                return jsonify({
                    'success': True,
                    'projectInfo': {
                        'projectName': project_name,
                        'displayName': display_name,
                        'outputDir': output_dir,
                        'kitFile': f"{project_name}.kit"
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.error
                }), 500

        except Exception as e:
            logger.error(f"Failed to create from template: {e}")
            return jsonify({'error': str(e)}), 500

    return template_bp

