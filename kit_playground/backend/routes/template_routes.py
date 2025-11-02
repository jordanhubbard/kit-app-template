"""
Template management routes for Kit Playground.
"""
import logging
import shutil
from pathlib import Path
from flask import Blueprint, jsonify, request

from tools.repoman.template_api import TemplateAPI

logger = logging.getLogger(__name__)

# Layer template to extension dependencies mapping
# Used for workaround of repo_kit_template bug (line 371 in repo.py)
LAYER_DEPENDENCIES = {
    'omni_default_streaming': [
        '"omni.kit.livestream.app" = {}  # WebRTC Streaming',
        '"omni.kit.livestream.webrtc" = {}  # WebRTC Core',
        '"omni.kit.livestream.core" = {}  # Livestream Core',
        '"omni.services.core" = {}  # Services Core',
        '"omni.services.transport.server.http" = {}  # HTTP server for client endpoints'
    ],
    'nvcf_streaming': [
        '"omni.services.livestream.session" = {}  # NVCF Streaming'
    ],
    'omni_gdn_streaming': [
        '"omni.kit.gfn" = {}  # GeForce NOW Streaming'
    ],
}

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


def _apply_layer_dependencies_workaround(
    kit_file_path: Path, layer_names: list
) -> bool:
    """
    Workaround for repo_kit_template bug (line 371 in repo.py).

    Manually adds layer dependencies and settings to the .kit file instead of using
    the broken add_layers() method in repo_kit_template.

    Args:
        kit_file_path: Path to the application's .kit file
        layer_names: List of layer template names to apply

    Returns:
        True if dependencies were added, False otherwise
    """
    if not kit_file_path.exists():
        logger.error(f"Kit file not found: {kit_file_path}")
        return False

    if not layer_names:
        return False

    try:
        # Read the .kit file
        content = kit_file_path.read_text()

        # Collect dependencies to add
        dependencies_to_add = []
        has_streaming_layer = False

        for layer_name in layer_names:
            if layer_name in LAYER_DEPENDENCIES:
                dependencies_to_add.extend(LAYER_DEPENDENCIES[layer_name])
                logger.info(f"Applying layer '{layer_name}' via workaround")

                # Check if this is a streaming layer
                if 'streaming' in layer_name.lower():
                    has_streaming_layer = True
            else:
                logger.warning(f"Unknown layer template '{layer_name}' - no dependency mapping available")

        if not dependencies_to_add:
            logger.warning("No dependencies to add for specified layers")
            return False

        # Check if dependencies already exist
        existing_deps = [dep for dep in dependencies_to_add if dep in content]
        if existing_deps:
            logger.info(f"Layer dependencies already present in {kit_file_path.name}")
            # Continue to check if settings need to be added
            if not has_streaming_layer:
                return False

        # Find [dependencies] section and add layers
        if "[dependencies]" in content:
            # Add after [dependencies] line
            layer_config = "\n# Layer dependencies (added via API workaround)\n"
            layer_config += "\n".join(dependencies_to_add) + "\n"

            new_content = content.replace("[dependencies]", f"[dependencies]{layer_config}")

            # If this is a streaming layer, add the port configuration settings
            if has_streaming_layer and 'settings.exts."omni.kit.livestream.webrtc"' not in new_content:
                streaming_settings = """
# Streaming configuration (added via API workaround)
[settings.exts."omni.kit.livestream.webrtc"]
port = 47995
enabled = true

[settings.app.livestream]
enabled = true
port = 47995
"""
                # Add settings at the end of the file
                new_content = new_content.rstrip() + "\n" + streaming_settings
                logger.info(f"Added streaming port configuration to {kit_file_path.name}")

            kit_file_path.write_text(new_content)

            logger.info(f"Successfully added {len(dependencies_to_add)} layer dependencies to {kit_file_path.name}")
            return True
        else:
            logger.error(f"Could not find [dependencies] section in {kit_file_path}")
            return False

    except Exception as e:
        logger.error("Error applying layer dependencies: %s", e)
        return False


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

    @bp.route('/layers', methods=['GET'])
    def list_layers():
        """
        List available layer templates (component type).

        Layers are templates that can be applied on top of base applications
        to add additional functionality (e.g., streaming capabilities).
        """
        try:
            # Get all templates
            all_templates = template_api.list_templates()

            # Filter for component/layer templates
            layers = [t for t in all_templates if t.type == 'component']

            # Group by category for easier UI organization
            categorized = {}
            for layer in layers:
                category = layer.category or 'other'
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(layer)

            return jsonify({
                'layers': layers,
                'categorized': categorized,
                'count': len(layers)
            })
        except Exception as e:
            logger.error(f"Error listing layers: {e}")
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

            # Handle layers (new feature)
            # WORKAROUND: repo_kit_template has a bug (line 371 in repo.py) that causes
            # TypeError when adding layers via playback. We apply layers manually after creation.
            selected_layers = data.get('layers', [])
            if selected_layers:
                logger.info("Layers requested: %s", selected_layers)
                logger.info(
                    "Using workaround for repo_kit_template bug - "
                    "will apply layers after creation"
                )
                # Note: We don't pass layers to create_application to avoid the bug

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

            # Create application
            # WORKAROUND: If layers are requested and the buggy repo_kit_template fails,
            # we recover gracefully since the app IS created before the error occurs
            result_dict = template_api.create_application(
                template_name=template_name,
                name=project_name,
                display_name=display_name,
                version=data.get('version', '1.0.0'),
                accept_license=True,
                no_register=False,
                **extra_params
            )

            # Log the result
            logger.info(f"Application creation result: {result_dict}")

            # WORKAROUND: Check if this is the repo_kit_template layer bug
            # The bug causes failure but the app IS created successfully
            if not result_dict.get('success') and selected_layers:
                error_msg = str(result_dict.get('error', ''))
                if "'NoneType' object is not iterable" in error_msg and "add_layers" in error_msg:
                    logger.warning("Detected repo_kit_template layer bug (line 371)")
                    logger.info("App was created despite error - recovering...")

                    # Check if app was actually created
                    app_dir = repo_root / "source" / "apps" / project_name
                    kit_file_path = app_dir / f"{project_name}.kit"

                    if kit_file_path.exists():
                        logger.info(f"✓ Confirmed app exists at {app_dir}")
                        # Reconstruct success result
                        result_dict = {
                            'success': True,
                            'app_name': project_name,
                            'display_name': display_name,
                            'app_dir': str(app_dir),
                            'kit_file': f"source/apps/{project_name}/{project_name}.kit",
                            'template_type': 'application',
                            'message': f"Application '{display_name}' created successfully (recovered from layer bug)"
                        }
                        logger.info("Successfully recovered from repo_kit_template bug")
                    else:
                        logger.error(f"App not found at {app_dir} - cannot recover")
                        # Keep the error result

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

                # WORKAROUND: Apply layers manually to avoid bug
                logger.info(f"DEBUG: selected_layers = {selected_layers}")
                logger.info(f"DEBUG: Checking if layers should be applied...")
                if selected_layers:
                    logger.info(
                        "Applying %d layer(s) via workaround...",
                        len(selected_layers)
                    )
                    layers_applied = _apply_layer_dependencies_workaround(
                        kit_file_abs, selected_layers
                    )
                    if layers_applied:
                        logger.info(
                            "Layers successfully applied to %s",
                            kit_file_abs.name
                        )
                    else:
                        logger.warning(
                            "Failed to apply some layers - check logs"
                        )

                # Kit App Streaming Note:
                # Streaming is implemented as an ApplicationLayerTemplate, not by modifying the .kit file.
                # To enable streaming, users should apply a streaming layer template:
                #   - default_stream.kit (uses omni.kit.livestream.app)
                #   - nvcf_stream.kit (uses omni.services.livestream.session for NVIDIA Cloud Functions)
                #   - gdn_stream.kit (uses omni.kit.gfn for GeForce NOW)
                #
                # The 'enable_streaming' parameter is deprecated and ignored.
                # Use streaming layer templates from templates/apps/streaming_configs/ instead.

                streaming_enabled = bool(
                    selected_layers and any(
                        'streaming' in layer.lower()
                        for layer in selected_layers
                    )
                )
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
