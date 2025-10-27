"""
Template management routes for Kit Playground.
"""
import logging
from pathlib import Path
from flask import Blueprint, jsonify, request

from tools.repoman.template_api import TemplateAPI

logger = logging.getLogger(__name__)

def create_template_routes(playground_app, template_api: TemplateAPI):
    """
    Create and configure template routes.

    Args:
        playground_app: PlaygroundApp instance
        template_api: TemplateAPI instance for template operations

    Returns:
        Flask Blueprint with template routes configured
    """
    # Create a NEW blueprint instance each time to avoid re-registration issues
    bp = Blueprint('templates', __name__, url_prefix='/api/templates')

    @bp.route('/list', methods=['GET'])
    @bp.route('', methods=['GET'])  # Alias: /api/templates
    def list_templates():
        """List all available templates."""
        try:
            templates = template_api.list_templates()
            return jsonify({'templates': templates})
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/get/<template_name>', methods=['GET'])
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

    @bp.route('/create', methods=['POST'])
    def create_from_template():
        """Create a new project from a template."""
        try:
            data = request.json
            template_name = data.get('template')
            project_name = data.get('name')
            display_name = data.get('displayName', project_name)
            enable_streaming = data.get('enableStreaming', False)

            # Get standalone flag - determines if we create a self-contained repo
            standalone = data.get('standalone', False)

            # CRITICAL: output_dir triggers standalone mode in template_engine.py
            # Only set it if explicitly requested AND standalone is True
            output_dir = None
            if standalone and data.get('outputDir'):
                output_dir = data.get('outputDir')

            if not template_name or not project_name:
                return jsonify({
                    'error': 'template and name are required'
                }), 400

            # Collect extra params
            extra_params = data.get('options', {}).copy()
            if 'perAppDeps' in data:
                extra_params['per_app_deps'] = data['perAppDeps']

            # Log the request for debugging
            logger.info(f"Creating project: template={template_name}, name={project_name}")
            logger.info(f"Using create_application() API - complete workflow (generate + execute + post-process)")
            logger.info(f"Extra params: {extra_params}")

            # Create application using the high-level API
            # This executes the full workflow: generate playback + execute + fix structure
            result_dict = template_api.create_application(
                template_name=template_name,
                name=project_name,
                display_name=display_name,
                version=data.get('version', '1.0.0'),
                accept_license=True,
                no_register=False,  # NOTE: --no-register flag not supported by replay command yet
                **extra_params
            )

            # Log the result
            logger.info(f"Application creation result: {result_dict}")

            if result_dict.get('success', False):
                # Extract paths from result
                app_dir = result_dict.get('app_dir', '')
                kit_file_path = result_dict.get('kit_file', '')

                # Convert relative kit_file to absolute if needed
                from pathlib import Path
                kit_file_abs = Path(kit_file_path)
                if not kit_file_abs.is_absolute():
                    kit_file_abs = Path(template_api.repo_root) / kit_file_path

                logger.info(f"Application created at: {app_dir}")
                logger.info(f".kit file path: {kit_file_abs}")

                # Enable Kit App Streaming if requested
                streaming_enabled = False
                if enable_streaming and kit_file_abs.exists():
                    try:
                        # Read the .kit file
                        kit_content = kit_file_abs.read_text()

                        # Check if streaming extensions are already present
                        streaming_exts = [
                            'omni.services.streaming.webrtc',
                            'omni.kit.streamhelper'
                        ]

                        needs_update = False
                        for ext in streaming_exts:
                            if ext not in kit_content:
                                needs_update = True
                                # Add the extension in the [dependencies] section
                                if '[dependencies]' in kit_content:
                                    parts = kit_content.split('[dependencies]', 1)
                                    if len(parts) == 2:
                                        kit_content = f'{parts[0]}[dependencies]\n"{ext}" = {{}}\n{parts[1]}'
                                else:
                                    kit_content += f'\n\n[dependencies]\n"{ext}" = {{}}\n'

                        if needs_update:
                            kit_file_abs.write_text(kit_content)
                            logger.info(f"Enabled Kit App Streaming extensions in {kit_file_abs}")
                            streaming_enabled = True
                        else:
                            logger.info(f"Streaming extensions already present")
                            streaming_enabled = True
                    except Exception as e:
                        logger.error(f"Failed to enable streaming extensions: {e}")
                        # Continue anyway - not critical

                return jsonify({
                    'success': True,
                    'projectInfo': {
                        'projectName': project_name,
                        'displayName': display_name,
                        'outputDir': app_dir,
                        'kitFile': str(kit_file_abs),  # Full absolute path to .kit file
                        'streaming': streaming_enabled,
                    },
                    'job_id': None  # For consistency with async endpoints
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result_dict.get('error', 'Unknown error occurred')
                }), 500

        except Exception as e:
            logger.error(f"Failed to create from template: {e}")
            return jsonify({'error': str(e)}), 500

    return bp
