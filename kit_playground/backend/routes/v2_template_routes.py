"""
V2 Template API routes for Kit Playground.
These routes provide template management with icon support for the frontend.
"""
import logging
from pathlib import Path
from flask import Blueprint, jsonify, request, send_from_directory

from tools.repoman.template_api import TemplateAPI
from tools.repoman.repo_dispatcher import get_platform_build_dir

logger = logging.getLogger(__name__)

# Create blueprint
v2_template_bp = Blueprint('v2_templates', __name__, url_prefix='/api/v2/templates')


def create_v2_template_routes(playground_app, template_api: TemplateAPI, socketio=None):
    """
    Create and configure v2 template routes with icon support.

    Args:
        playground_app: PlaygroundApp instance
        template_api: TemplateAPI instance for template operations
        socketio: SocketIO instance for emitting logs to UI

    Returns:
        Flask Blueprint with v2 template routes configured
    """

    @v2_template_bp.route('', methods=['GET'])
    def list_templates_v2():
        """List all templates with icon URLs (excluding components which can't be standalone)."""
        try:
            template_type = request.args.get('type')
            category = request.args.get('category')
            templates = template_api.list_templates(template_type, category)

            repo_root = Path(__file__).parent.parent.parent.parent

            # Convert to dict for JSON serialization with icon support
            # Filter out components since they can't be instantiated as standalone projects
            result = []
            for t in templates:
                # Skip components - they can only be used within applications
                if t.type == 'component':
                    continue
                # Check for icon file in template directory
                icon_url = None

                # Try multiple possible directory names - look for icon file, not just directory
                possible_names = [t.name]
                # Strip 'omni_' prefix if present (omni_usd_viewer -> usd_viewer)
                if t.name.startswith('omni_'):
                    possible_names.append(t.name[5:])
                # Strip '_setup' or '_messaging' suffixes
                base_name = t.name.replace('_setup', '').replace('_messaging', '')
                if base_name not in possible_names:
                    possible_names.append(base_name)

                if t.type in ['application', 'microservice']:
                    for name in possible_names:
                        test_dir = repo_root / 'templates' / 'apps' / name
                        icon_path = test_dir / 'assets' / 'icon.png'
                        if icon_path.exists():
                            icon_url = f'/api/v2/templates/{t.name}/icon'
                            break
                    # Also try microservices directory
                    if not icon_url:
                        for name in possible_names:
                            test_dir = repo_root / 'templates' / 'microservices' / name
                            icon_path = test_dir / 'assets' / 'icon.png'
                            if icon_path.exists():
                                icon_url = f'/api/v2/templates/{t.name}/icon'
                                break
                elif t.type == 'extension':
                    for name in possible_names:
                        test_dir = repo_root / 'templates' / 'extensions' / name
                        icon_path = test_dir / 'template' / 'data' / 'icon.png'
                        if icon_path.exists():
                            icon_url = f'/api/v2/templates/{t.name}/icon'
                            break
                elif t.type == 'component':
                    # Components might not have icons, but check anyway
                    for name in possible_names:
                        test_dir = repo_root / 'templates' / 'components' / name
                        icon_path = test_dir / 'template' / 'data' / 'icon.png'
                        if icon_path.exists():
                            icon_url = f'/api/v2/templates/{t.name}/icon'
                            break

                result.append({
                    'id': t.name,
                    'name': t.name,
                    'displayName': t.display_name,
                    'type': t.type,
                    'category': t.category,
                    'description': t.description,
                    'version': t.version,
                    'tags': t.tags,
                    'documentation': t.documentation,
                    'icon': icon_url,
                    'thumbnail': icon_url  # Use same icon for thumbnail for now
                })
            return jsonify(result)
        except Exception as e:
            logger.error(f"Failed to list templates: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @v2_template_bp.route('/<template_id>/icon', methods=['GET'])
    def get_template_icon(template_id):
        """Serve template icon."""
        try:
            repo_root = Path(__file__).parent.parent.parent.parent

            # Try multiple possible directory names
            possible_names = [template_id]
            # Strip 'omni_' prefix if present (omni_usd_viewer -> usd_viewer)
            if template_id.startswith('omni_'):
                possible_names.append(template_id[5:])
            # Strip '_setup' or '_messaging' suffixes
            base_name = template_id.replace('_setup', '').replace('_messaging', '')
            if base_name not in possible_names:
                possible_names.append(base_name)

            # Try application templates first
            icon_path = None
            for name in possible_names:
                test_path = repo_root / 'templates' / 'apps' / name / 'assets' / 'icon.png'
                if test_path.exists():
                    icon_path = test_path
                    break

            # Try microservices
            if not icon_path:
                for name in possible_names:
                    test_path = repo_root / 'templates' / 'microservices' / name / 'assets' / 'icon.png'
                    if test_path.exists():
                        icon_path = test_path
                        break

            # Try extension templates if not found
            if not icon_path:
                for name in possible_names:
                    test_path = repo_root / 'templates' / 'extensions' / name / 'template' / 'data' / 'icon.png'
                    if test_path.exists():
                        icon_path = test_path
                        break

            # Try components
            if not icon_path:
                for name in possible_names:
                    test_path = repo_root / 'templates' / 'components' / name / 'template' / 'data' / 'icon.png'
                    if test_path.exists():
                        icon_path = test_path
                        break

            if icon_path and icon_path.exists():
                return send_from_directory(icon_path.parent, icon_path.name)
            else:
                # Return 404 with JSON error
                return jsonify({'error': 'Icon not found'}), 404
        except Exception as e:
            logger.error(f"Failed to get template icon: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @v2_template_bp.route('/<template_id>/docs', methods=['GET'])
    def get_template_docs(template_id):
        """Get template documentation."""
        try:
            templates = template_api.list_templates()
            template = next((t for t in templates if t.name == template_id), None)

            if not template:
                return jsonify({'error': 'Template not found'}), 404

            return jsonify({
                'name': template.name,
                'displayName': template.display_name,
                'type': template.type,
                'category': template.category,
                'description': template.description,
                'version': template.version,
                'documentation': template.documentation or f"# {template.display_name}\n\n{template.description}",
                'tags': template.tags
            })
        except Exception as e:
            logger.error(f"Failed to get template docs: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @v2_template_bp.route('/generate', methods=['POST'])
    def generate_template_v2():
        """Generate a template using unified API (new high-level method)."""
        try:
            data = request.json

            # Extract request parameters
            template_name = data.get('templateName')
            name = data.get('name')
            display_name = data.get('displayName', name)
            version = data.get('version', '0.1.0')

            if not template_name or not name:
                return jsonify({
                    'error': 'templateName and name are required'
                }), 400

            # Emit log to UI for user feedback
            if socketio:
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'build',
                    'message': f'Creating project: {display_name}'
                })
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'build',
                    'message': f'Template: {template_name}'
                })

            # Use new high-level API - handles everything cleanly
            result = template_api.create_application(
                template_name=template_name,
                name=name,
                display_name=display_name,
                version=version,
                accept_license=True,  # Auto-accept for GUI
                no_register=False,  # Use default registration
                **data.get('options', {})
            )

            if result.get('success', False):
                # Success! Emit to UI
                if socketio:
                    socketio.emit('log', {
                        'level': 'success',
                        'source': 'build',
                        'message': f'Project created successfully: {display_name}'
                    })

                logger.info(f"✓ Project created: {result['app_dir']}")
                logger.info(f"✓ Kit file: {result['kit_file']}")

                # Calculate paths for UI response
                repo_root = Path(__file__).parent.parent.parent.parent
                platform_build_dir = get_platform_build_dir(repo_root, 'release')
                relative_output_dir = str(
                    (platform_build_dir / 'apps').relative_to(repo_root)
                )
                kit_file_path = f"{relative_output_dir}/{name}/{name}.kit"

                return jsonify({
                    'success': True,
                    'outputDir': relative_output_dir,
                    'projectInfo': {
                        'projectName': name,
                        'displayName': display_name,
                        'outputDir': relative_output_dir,
                        'kitFile': kit_file_path,
                        'kitFileName': f"{name}.kit"
                    },
                    'message': result.get('message'),
                    'playbackFile': result.get('playback_file', '')
                })
            else:
                # Failed
                error = result.get('error', 'Unknown error')
                if socketio:
                    socketio.emit('log', {
                        'level': 'error',
                        'source': 'build',
                        'message': f'Failed to create project: {error}'
                    })
                return jsonify({
                    'success': False,
                    'error': error
                }), 500

        except Exception as e:
            logger.error(f"Failed to generate template: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return v2_template_bp
