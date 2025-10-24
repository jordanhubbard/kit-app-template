"""
Template management routes for Kit Playground.
"""
import logging
from flask import Blueprint, jsonify, request

from tools.repoman.template_api import (
    TemplateAPI,
    TemplateGenerationRequest
)

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
    @template_bp.route('', methods=['GET'])  # Alias: /api/templates
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
            # Use None as default to match CLI behavior (source/apps)
            output_dir = data.get('outputDir', None)
            enable_streaming = data.get('enableStreaming', False)

            if not template_name or not project_name:
                return jsonify({
                    'error': 'template and name are required'
                }), 400

            # Prepare generation request
            gen_request = TemplateGenerationRequest(
                template_name=template_name,
                name=project_name,  # Correct parameter name
                display_name=display_name,
                version=data.get('version', '1.0.0'),
                output_dir=output_dir,  # Correct parameter name
                accept_license=True,  # Auto-accept for GUI
                force_overwrite=True,  # Auto-overwrite for GUI (no stdin for prompts)
                extra_params=data.get('options', {})  # Correct parameter name
            )

            # Generate project
            result = template_api.generate_template(gen_request)

            if result.success:
                # Fix repo.toml: The template system adds entries to the static apps list,
                # but we use dynamic discovery via app_discovery_paths instead.
                # Clear the static apps list to prevent build errors.
                try:
                    import toml
                    from pathlib import Path
                    repo_toml_path = Path(template_api.repo_root) / "repo.toml"
                    if repo_toml_path.exists():
                        with open(repo_toml_path, 'r') as f:
                            repo_config = toml.load(f)

                        # Clear the static apps list (line 113 in repo.toml)
                        if 'apps' in repo_config:
                            repo_config['apps'] = []

                            with open(repo_toml_path, 'w') as f:
                                toml.dump(repo_config, f)

                            logger.info("Cleared static apps list in repo.toml (using dynamic discovery)")
                except Exception as e:
                    logger.warning(f"Failed to fix repo.toml after project creation: {e}")
                    # Continue anyway - this is not critical

                # Enable Kit App Streaming if requested
                streaming_enabled = False
                if enable_streaming:
                    try:
                        from pathlib import Path
                        # Find the generated .kit file
                        repo_root = Path(template_api.repo_root)
                        kit_file_path = repo_root / "source" / "apps" / project_name / f"{project_name}.kit"

                        if kit_file_path.exists():
                            # Read the .kit file
                            with open(kit_file_path, 'r') as f:
                                kit_content = f.read()

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
                                    # Find the [dependencies] section
                                    if '[dependencies]' in kit_content:
                                        # Insert after [dependencies]
                                        parts = kit_content.split('[dependencies]', 1)
                                        if len(parts) == 2:
                                            # Add the extension at the beginning of dependencies
                                            kit_content = f'{parts[0]}[dependencies]\n"{ext}" = {{}}\n{parts[1]}'
                                    else:
                                        # Add dependencies section if it doesn't exist
                                        kit_content += f'\n\n[dependencies]\n"{ext}" = {{}}\n'

                            if needs_update:
                                # Write back the updated .kit file
                                with open(kit_file_path, 'w') as f:
                                    f.write(kit_content)
                                logger.info(f"Enabled Kit App Streaming extensions in {kit_file_path}")
                                streaming_enabled = True
                            else:
                                logger.info(f"Streaming extensions already present in {kit_file_path}")
                                streaming_enabled = True
                        else:
                            logger.warning(f".kit file not found at {kit_file_path}")
                    except Exception as e:
                        logger.error(f"Failed to enable streaming extensions: {e}")
                        # Continue anyway - not critical

                return jsonify({
                    'success': True,
                    'projectInfo': {
                        'projectName': project_name,
                        'displayName': display_name,
                        'outputDir': output_dir,
                        'kitFile': f"{project_name}.kit",
                        'streaming': streaming_enabled
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
