"""
V2 Template API routes for Kit Playground.
These routes provide template management with icon support for the frontend.
"""
import logging
import subprocess
from pathlib import Path
from flask import Blueprint, jsonify, request, send_from_directory

from tools.repoman.template_api import TemplateAPI, TemplateGenerationRequest
from tools.repoman.repo_dispatcher import _fix_application_structure, get_platform_build_dir

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
        """List all templates with icon URLs."""
        try:
            template_type = request.args.get('type')
            category = request.args.get('category')
            templates = template_api.list_templates(template_type, category)

            repo_root = Path(__file__).parent.parent.parent.parent

            # Convert to dict for JSON serialization with icon support
            result = []
            for t in templates:
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
        """Generate a template using unified API."""
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

            # Don't pass output_dir - this creates the app normally in the current repo
            # The template system will create in source/apps then automatically restructure
            # and move to _build/apps/{name}/{name}.kit (flat structure, same as CLI)

            # Prepare generation request
            req = TemplateGenerationRequest(
                template_name=template_name,
                name=name,
                display_name=display_name,
                version=version,
                output_dir=None,  # Use default repo behavior (source/apps -> _build/apps)
                accept_license=True,  # Auto-accept for GUI
                force_overwrite=True,  # Skip directory overwrite confirmation for GUI
                extra_params=data.get('options', {})
            )

            # Generate project (creates playback file)
            result = template_api.generate_template(req)

            if result.success:
                # Execute the playback file to actually create the project files
                repo_root = Path(__file__).parent.parent.parent.parent
                replay_cmd = [
                    str(repo_root / 'repo.sh'),
                    'template',
                    'replay',
                    result.playback_file  # Positional argument, not --playback-file
                ]

                logger.info("=" * 80)
                logger.info(f"TEMPLATE CREATION: {display_name} (template: {template_name})")
                logger.info(f"Executing replay command: {' '.join(replay_cmd)}")
                logger.info(f"Playback file: {result.playback_file}")
                logger.info(f"Playback file exists: {Path(result.playback_file).exists()}")
                logger.info(f"Working directory: {repo_root}")
                logger.info("=" * 80)

                try:
                    # Emit log to UI including the CLI command
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
                        # Show the CLI command for reproducibility
                        socketio.emit('log', {
                            'level': 'info',
                            'source': 'build',
                            'message': f'$ cd {repo_root}'
                        })
                        socketio.emit('log', {
                            'level': 'info',
                            'source': 'build',
                            'message': f'$ {" ".join(replay_cmd)}'
                        })

                    replay_result = subprocess.run(
                        replay_cmd,
                        cwd=str(repo_root),
                        capture_output=True,
                        text=True,
                        timeout=120  # 2 minutes timeout for template replay
                    )

                    logger.info(f"Replay command exit code: {replay_result.returncode}")

                    # Emit replay output to UI
                    if replay_result.stdout:
                        logger.info(f"Replay stdout:\n{replay_result.stdout}")
                        if socketio:
                            for line in replay_result.stdout.strip().split('\n'):
                                if line:
                                    socketio.emit('log', {
                                        'level': 'info',
                                        'source': 'build',
                                        'message': line
                                    })

                    if replay_result.stderr:
                        logger.info(f"Replay stderr:\n{replay_result.stderr}")
                        if socketio:
                            for line in replay_result.stderr.strip().split('\n'):
                                if line:
                                    socketio.emit('log', {
                                        'level': 'warning',
                                        'source': 'build',
                                        'message': line
                                    })

                    logger.info("=" * 80)

                    if replay_result.returncode != 0:
                        error_msg = f"Template replay failed with exit code {replay_result.returncode}"
                        if replay_result.stderr:
                            error_msg += f": {replay_result.stderr}"
                        elif replay_result.stdout:
                            error_msg += f": {replay_result.stdout}"

                        logger.error(error_msg)
                        return jsonify({
                            'success': False,
                            'error': error_msg,
                            'stdout': replay_result.stdout,
                            'stderr': replay_result.stderr,
                            'exitCode': replay_result.returncode
                        }), 500

                    # Post-process: Move files from source/apps to _build/apps
                    # The replay creates files in source/apps but they need to be
                    # restructured in _build/apps/{name}/{name}.kit format
                    try:
                        logger.info("Post-processing: Moving files from source/apps to _build/apps")
                        if socketio:
                            socketio.emit('log', {
                                'level': 'info',
                                'source': 'build',
                                'message': 'Finalizing project structure...'
                            })

                        # Read the playback file to get configuration
                        try:
                            import tomllib
                            with open(result.playback_file, 'rb') as f:
                                playback_data = tomllib.load(f)
                        except ImportError:
                            import toml
                            with open(result.playback_file, 'r') as f:
                                playback_data = toml.load(f)

                        # Call the restructuring function
                        # This moves apps to platform-specific directory: _build/{platform}-{arch}/release/apps/
                        app_dir = _fix_application_structure(repo_root, playback_data)
                        logger.info("✓ Application structure fixed")

                        # Fix repo.toml: The template system adds entries to the static apps list,
                        # but we use dynamic discovery via app_discovery_paths instead.
                        # Clear the static apps list to prevent build errors.
                        # We use regex replacement to preserve formatting and comments.
                        try:
                            import re
                            repo_toml_path = repo_root / "repo.toml"
                            if repo_toml_path.exists():
                                with open(repo_toml_path, 'r') as f:
                                    content = f.read()

                                # Find and replace the apps = [...] line with apps = []
                                # This regex matches: apps = ["anything"] or apps = ['anything']
                                # and replaces it with apps = []
                                pattern = r'^apps\s*=\s*\[.*?\]'
                                replacement = 'apps = []'

                                new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

                                if count > 0:
                                    with open(repo_toml_path, 'w') as f:
                                        f.write(new_content)
                                    logger.info(f"✓ Cleared static apps list in repo.toml ({count} replacements)")
                                else:
                                    logger.info("✓ No apps list to clear in repo.toml")
                        except Exception as e:
                            logger.warning(f"Failed to fix repo.toml after project creation: {e}")
                            # Continue anyway - this is not critical

                        if socketio:
                            socketio.emit('log', {
                                'level': 'success',
                                'source': 'build',
                                'message': f'Project created successfully: {display_name}'
                            })

                    except Exception as e:
                        error_msg = f"Failed to restructure application: {str(e)}"
                        logger.error(error_msg, exc_info=True)
                        return jsonify({
                            'success': False,
                            'error': error_msg,
                            'replayStdout': replay_result.stdout
                        }), 500

                except subprocess.TimeoutExpired:
                    error_msg = "Template replay timed out after 120 seconds"
                    logger.error(error_msg)
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 500
                except Exception as e:
                    error_msg = f"Failed to execute replay command: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 500

                # Apps are created in source/apps (real location)
                # Build system symlinks: source/apps → _build/{platform}/{config}/apps
                # Return the symlinked path to UI for consistency with build artifacts
                platform_build_dir = get_platform_build_dir(repo_root, 'release')

                # Real location (source/apps)
                project_dir = repo_root / "source" / "apps" / name
                kit_file = project_dir / f"{name}.kit"

                # Symlinked location (what UI and build system use)
                relative_output_dir = str((platform_build_dir / 'apps').relative_to(repo_root))
                kit_file_path = f"{relative_output_dir}/{name}/{name}.kit"

                if not project_dir.exists():
                    error_msg = f"Project directory was not created: {project_dir}"
                    logger.error(error_msg)
                    return jsonify({
                        'success': False,
                        'error': error_msg,
                        'replayStdout': replay_result.stdout,
                        'replayStderr': replay_result.stderr
                    }), 500

                if not kit_file.exists():
                    error_msg = f"Kit configuration file was not created: {kit_file}"
                    logger.error(error_msg)
                    return jsonify({
                        'success': False,
                        'error': error_msg,
                        'replayStdout': replay_result.stdout,
                        'replayStderr': replay_result.stderr
                    }), 500

                logger.info(f"✓ Project created successfully: {project_dir}")
                logger.info(f"✓ Kit file exists: {kit_file}")
                logger.info("=" * 80)

                return jsonify({
                    'success': True,
                    'outputDir': relative_output_dir,  # Platform-specific: _build/linux-x86_64/release/apps
                    'projectInfo': {
                        'projectName': name,
                        'displayName': display_name,
                        'outputDir': relative_output_dir,
                        'kitFile': kit_file_path,  # Relative path: _build/linux-x86_64/release/apps/name/name.kit
                        'kitFileName': f"{name}.kit"
                    },
                    'message': f"Project '{display_name}' created successfully",
                    'playbackFile': result.playback_file,
                    'replayOutput': replay_result.stdout
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.error
                }), 500

        except Exception as e:
            logger.error(f"Failed to generate template: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return v2_template_bp
