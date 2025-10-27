"""
Template management routes for Kit Playground.
"""
import logging
import shutil
from pathlib import Path
from flask import Blueprint, jsonify, request

from tools.repoman.template_api import TemplateAPI

logger = logging.getLogger(__name__)

# Template-to-extension mapping
# Maps template names to the extension patterns they create
TEMPLATE_EXTENSION_PATTERNS = {
    # Application templates (also create setup extensions)
    'omni_usd_composer': [
        '*.usd_composer_setup',
        '*_usd_composer_setup',
        '*.composer_setup',
        '*_composer_setup',
    ],
    'omni_usd_viewer': [
        '*.usd_viewer_setup',
        '*_usd_viewer_setup',
        '*.viewer_setup',
        '*_viewer_setup',
    ],
    'kit_base_editor': [
        '*.usd_editor_setup',
        '*_usd_editor_setup',
        '*.editor_setup',
        '*_editor_setup',
    ],
    'omni_usd_explorer': [
        '*.usd_explorer_setup',
        '*_usd_explorer_setup',
        '*.explorer_setup',
        '*_explorer_setup',
    ],
    # Setup extension templates (create the same patterns)
    'omni_usd_composer_setup': [
        '*.usd_composer_setup',
        '*_usd_composer_setup',
        '*.composer_setup',
        '*_composer_setup',
    ],
    'omni_usd_viewer_setup': [
        '*.usd_viewer_setup',
        '*_usd_viewer_setup',
        '*.viewer_setup',
        '*_viewer_setup',
    ],
    'omni_usd_editor_setup': [
        '*.usd_editor_setup',
        '*_usd_editor_setup',
        '*.editor_setup',
        '*_editor_setup',
    ],
    'omni_usd_explorer_setup': [
        '*.usd_explorer_setup',
        '*_usd_explorer_setup',
        '*.explorer_setup',
        '*_explorer_setup',
    ],
    # Add more template mappings as needed
}

def _clean_conflicting_extensions(template_name: str, repo_root: Path) -> list:
    """
    Clean extensions that would conflict with the template being created.

    This is a workaround for Kit SDK's template replay system which errors
    when encountering existing directories instead of reusing them.

    Args:
        template_name: Name of the template being created
        repo_root: Root directory of the repository

    Returns:
        List of extension names that were removed
    """
    extensions_dir = repo_root / 'source' / 'extensions'
    if not extensions_dir.exists():
        return []

    patterns = TEMPLATE_EXTENSION_PATTERNS.get(template_name, [])
    if not patterns:
        logger.debug(f"No known extension patterns for template: {template_name}")
        return []

    removed = []
    for pattern in patterns:
        for ext_dir in extensions_dir.glob(pattern):
            if not ext_dir.is_dir():
                continue

            try:
                logger.info(f"Pre-cleaning conflicting extension: {ext_dir.name}")
                shutil.rmtree(ext_dir)
                removed.append(ext_dir.name)
            except Exception as e:
                logger.error(f"Failed to pre-clean extension {ext_dir.name}: {e}")

    if removed:
        logger.info(f"Pre-cleaned {len(removed)} extension(s) for template {template_name}")

    return removed

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

            # PRE-CLEAN: Remove any conflicting extensions before creation
            # This prevents "directory already exists" errors from the Kit SDK's template replay
            repo_root = Path(__file__).parent.parent.parent.parent
            removed_extensions = _clean_conflicting_extensions(template_name, repo_root)
            if removed_extensions:
                logger.info(f"Pre-cleaned extensions to avoid conflicts: {removed_extensions}")

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
                # (Path already imported at module level)
                kit_file_abs = Path(kit_file_path)
                if not kit_file_abs.is_absolute():
                    kit_file_abs = Path(template_api.repo_root) / kit_file_path

                logger.info(f"Application created at: {app_dir}")
                logger.info(f".kit file path: {kit_file_abs}")

                # Kit App Streaming Note:
                # Streaming is implemented as an ApplicationLayerTemplate, not by modifying the .kit file.
                # To enable streaming, users should apply a streaming layer template:
                #   - default_stream.kit (uses omni.kit.livestream.app)
                #   - nvcf_stream.kit (uses omni.services.livestream.session for NVIDIA Cloud Functions)
                #   - gdn_stream.kit (uses omni.kit.gfn for GeForce NOW)
                #
                # The 'enable_streaming' parameter is deprecated and ignored.
                # Use streaming layer templates from templates/apps/streaming_configs/ instead.

                streaming_enabled = False
                streaming_warning = None

                if enable_streaming:
                    logger.warning("Kit App Streaming requested via 'enable_streaming' parameter.")
                    logger.warning("This parameter is DEPRECATED. Streaming must be configured as a layer template.")
                    logger.warning("Available streaming layers:")
                    logger.warning("  - default_stream.kit (omni.kit.livestream.app)")
                    logger.warning("  - nvcf_stream.kit (omni.services.livestream.session for NVCF)")
                    logger.warning("  - gdn_stream.kit (omni.kit.gfn for GeForce NOW)")
                    logger.warning("For remote preview without streaming, use Xpra mode instead.")

                    streaming_warning = (
                        "Note: Kit App Streaming must be configured as a layer template, not via this parameter. "
                        "Use streaming layer templates from templates/apps/streaming_configs/ "
                        "(default_stream.kit, nvcf_stream.kit, or gdn_stream.kit). "
                        "For simple remote preview, use Xpra mode instead."
                    )

                response_data = {
                    'success': True,
                    'projectInfo': {
                        'projectName': project_name,
                        'displayName': display_name,
                        'outputDir': app_dir,
                        'kitFile': str(kit_file_abs),  # Full absolute path to .kit file
                        'streaming': streaming_enabled,
                    },
                    'job_id': None  # For consistency with async endpoints
                }

                if streaming_warning:
                    response_data['warning'] = streaming_warning

                return jsonify(response_data)
            else:
                return jsonify({
                    'success': False,
                    'error': result_dict.get('error', 'Unknown error occurred')
                }), 500

        except Exception as e:
            logger.error(f"Failed to create from template: {e}")
            return jsonify({'error': str(e)}), 500

    return bp
