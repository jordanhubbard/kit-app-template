"""
Project build and run routes for Kit Playground.
"""
import logging
import subprocess
import threading
import shutil
from pathlib import Path
from typing import Dict, Optional

from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)

# Create blueprint
project_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


def create_project_routes(
    playground_app,
    socketio: SocketIO,
    processes: Dict[str, subprocess.Popen],
    xpra_manager,
    security_validator
):
    """
    Create and configure project routes.

    Args:
        playground_app: PlaygroundApp instance
        socketio: SocketIO instance for real-time logging
        processes: Dictionary tracking running processes
        xpra_manager: XpraManager instance
        security_validator: Object with security validation methods

    Returns:
        Flask Blueprint with project routes configured
    """

    @project_bp.route('/build', methods=['POST'])
    def build_project():
        """Build a Kit project using repo.sh wrapper from the app directory."""
        try:
            data = request.json
            project_path = data.get('projectPath')
            project_name = data.get('projectName')

            # SECURITY: Validate project_name to prevent command injection
            if project_name and not security_validator._is_safe_project_name(project_name):
                return jsonify({
                    'error': 'Invalid project name. Avoid special characters like ; & | $ ` ( ) < > \\ " \' and control characters.'
                }), 400

            repo_root = Path(__file__).parent.parent.parent.parent
            logger.info("Building project: %s", project_name)

            # Use the project-specific repo.sh wrapper
            if project_path:
                # SECURITY: Validate and normalize project_path
                app_dir = security_validator._validate_project_path(repo_root, project_path)
                if not app_dir:
                    return jsonify({'error': 'Invalid project path'}), 400

                wrapper_script = app_dir / 'repo.sh'

                if wrapper_script.exists():
                    logger.info("Using wrapper from: %s", app_dir)
                    result = subprocess.run(
                        ['./repo.sh', 'build', '--config', 'release'],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=str(app_dir)
                    )
                else:
                    logger.info("Wrapper not found, using repo root")
                    result = subprocess.run(
                        [str(repo_root / 'repo.sh'), 'build', '--config', 'release'],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=str(repo_root)
                    )
            else:
                result = subprocess.run(
                    [str(repo_root / 'repo.sh'), 'build', '--config', 'release'],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(repo_root)
                )

            # Log build output (full output, not truncated)
            logger.info("Build stdout: %s", result.stdout if result.stdout else 'none')
            if result.stderr:
                logger.info("Build stderr: %s", result.stderr)

            # Emit build logs line by line to console
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        socketio.emit('log', {
                            'level': 'info',
                            'source': 'build',
                            'message': line
                        })

            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line:
                        socketio.emit('log', {
                            'level': 'error',
                            'source': 'build',
                            'message': line
                        })

            success = result.returncode == 0
            return jsonify({
                'success': success,
                'output': result.stdout,
                'error': result.stderr if not success else None
            })
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Build timeout (300s)'}), 500
        except Exception as e:
            logger.error(f"Failed to build project: {e}")
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/run', methods=['POST'])
    def run_project():
        """Run a Kit project using repo.sh launch."""
        try:
            data = request.json
            project_path = data.get('projectPath')
            project_name = data.get('projectName')
            use_xpra = data.get('useXpra', False)

            if not project_name:
                return jsonify({'error': 'projectName required'}), 400

            # SECURITY: Validate project_name
            if not security_validator._is_safe_project_name(project_name):
                return jsonify({
                    'error': 'Invalid project name. Avoid special characters like ; & | $ ` ( ) < > \\ " \' and control characters.'
                }), 400

            kit_file = f"{project_name}.kit"
            repo_root = Path(__file__).parent.parent.parent.parent
            logger.info(f"Launching kit application: {kit_file} (Xpra: {use_xpra})")

            preview_url = None

            if use_xpra:
                # Launch with Xpra for browser preview
                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': 'Starting Xpra session for browser preview...'
                })

                session_id = f"project_{project_name}"
                session = xpra_manager.create_session(session_id)

                if not session:
                    socketio.emit('log', {
                        'level': 'error',
                        'source': 'runtime',
                        'message': 'Failed to start Xpra. Is Xpra installed? See XPRA_SETUP.md'
                    })
                    return jsonify({
                        'success': False,
                        'error': 'Failed to start Xpra session. Please check if Xpra is installed.'
                    }), 500

                kit_script = repo_root / '_build' / 'linux-x86_64' / 'release' / f'{kit_file}.sh'
                if not kit_script.exists():
                    socketio.emit('log', {
                        'level': 'error',
                        'source': 'runtime',
                        'message': f'Kit script not found: {kit_script}. Did you build the project?'
                    })
                    xpra_manager.stop_session(session_id)
                    return jsonify({
                        'success': False,
                        'error': 'Kit script not found. Please build the project first.'
                    }), 400

                if session.launch_app(str(kit_script)):
                    server_host = request.host.split(':')[0]
                    preview_url = xpra_manager.get_session_url(session_id, host=server_host)
                    socketio.emit('log', {
                        'level': 'success',
                        'source': 'runtime',
                        'message': f'Application launched in Xpra. Preview: {preview_url}'
                    })
                else:
                    socketio.emit('log', {
                        'level': 'error',
                        'source': 'runtime',
                        'message': 'Failed to launch application in Xpra session'
                    })
                    xpra_manager.stop_session(session_id)
                    return jsonify({'success': False, 'error': 'Failed to launch app in Xpra'}), 500

            else:
                # Direct launch (normal mode)
                if project_path:
                    # SECURITY: Validate and normalize project_path
                    app_dir = security_validator._validate_project_path(repo_root, project_path)
                    if not app_dir:
                        return jsonify({'error': 'Invalid project path'}), 400

                    wrapper_script = app_dir / 'repo.sh'

                    if wrapper_script.exists():
                        logger.info("Launching from: %s", app_dir)
                        process = subprocess.Popen(
                            ['./repo.sh', 'launch', kit_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            cwd=str(app_dir)
                        )
                    else:
                        process = subprocess.Popen(
                            [str(repo_root / 'repo.sh'), 'launch', kit_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            cwd=str(repo_root)
                        )
                else:
                    process = subprocess.Popen(
                        [str(repo_root / 'repo.sh'), 'launch', kit_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=str(repo_root)
                    )

                # SECURITY: Limit number of concurrent processes
                if len(processes) >= 10:
                    return jsonify({
                        'error': 'Too many running processes. Please stop some before starting new ones.'
                    }), 429

                processes[project_name] = process

                socketio.emit('log', {
                    'level': 'success',
                    'source': 'runtime',
                    'message': f'Launching {kit_file}...'
                })

                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': 'Note: The application window will appear on the host machine.'
                })

                # Start a thread to stream output
                def stream_output():
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            socketio.emit('log', {
                                'level': 'info',
                                'source': 'runtime',
                                'message': line.rstrip()
                            })
                    for line in iter(process.stderr.readline, ''):
                        if line:
                            socketio.emit('log', {
                                'level': 'error',
                                'source': 'runtime',
                                'message': line.rstrip()
                            })

                threading.Thread(target=stream_output, daemon=True).start()

            return jsonify({
                'success': True,
                'previewUrl': preview_url
            })
        except Exception as e:
            logger.error(f"Failed to run project: {e}")
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/discover', methods=['GET'])
    def discover_projects():
        """Discover existing Kit projects in a directory."""
        try:
            path = request.args.get('path')
            if not path:
                return jsonify({'error': 'path parameter required'}), 400

            # Basic path validation
            validated_path = security_validator._validate_filesystem_path(path)
            if not validated_path:
                return jsonify({'error': 'Invalid or inaccessible path'}), 400

            # Find .kit files in the directory
            projects = []
            if validated_path.exists() and validated_path.is_dir():
                for kit_file in validated_path.glob('*/*.kit'):
                    project_name = kit_file.stem
                    project_dir = kit_file.parent

                    projects.append({
                        'id': project_name,
                        'name': project_name,
                        'displayName': project_name,
                        'path': str(project_dir.relative_to(validated_path)),
                        'kitFile': str(kit_file),
                        'relativePath': str(project_dir.relative_to(validated_path)),
                        'status': 'ready'
                    })

            return jsonify({'projects': projects})
        except Exception as e:
            logger.error(f"Failed to discover projects: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/stop', methods=['POST'])
    def stop_project_body():
        """Stop a running project (accepts project name in request body)."""
        try:
            data = request.json
            project_name = data.get('projectName')

            if not project_name:
                return jsonify({'error': 'projectName required'}), 400

            if project_name in processes:
                process = processes[project_name]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                del processes[project_name]

                socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'Stopped project: {project_name}'
                })

                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Project not running'}), 404
        except Exception as e:
            logger.error(f"Failed to stop project: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/stop/<project_name>', methods=['POST'])
    def stop_project(project_name: str):
        """Stop a running project (legacy endpoint with URL parameter)."""
        try:
            if project_name in processes:
                process = processes[project_name]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                del processes[project_name]
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Project not running'}), 404
        except Exception as e:
            logger.error(f"Failed to stop project: {e}")
            return jsonify({'error': str(e)}), 500

    @project_bp.route('/delete', methods=['POST'])
    def delete_project():
        """Delete a project directory and all its contents."""
        try:
            data = request.json
            project_id = data.get('projectId')
            projects_path = data.get('projectsPath', '_build/apps')

            if not project_id:
                return jsonify({'error': 'projectId required'}), 400

            # SECURITY: Validate project_id to prevent path traversal
            if not security_validator._is_safe_project_name(project_id):
                return jsonify({
                    'error': 'Invalid project ID. Avoid special characters and path traversal attempts.'
                }), 400

            # Get repo root
            repo_root = Path(__file__).parent.parent.parent.parent

            # Validate projects path
            validated_projects_path = security_validator._validate_filesystem_path(projects_path)
            if not validated_projects_path:
                return jsonify({'error': 'Invalid projects path'}), 400

            # Construct project directory path
            project_dir = validated_projects_path / project_id

            # Security check: Ensure project_dir is within the validated projects path
            try:
                project_dir = project_dir.resolve()
                validated_projects_path = validated_projects_path.resolve()
                if not str(project_dir).startswith(str(validated_projects_path)):
                    return jsonify({'error': 'Invalid project path - outside projects directory'}), 403
            except Exception as e:
                logger.error(f"Path resolution error: {e}")
                return jsonify({'error': 'Invalid project path'}), 400

            # Check if project directory exists
            if not project_dir.exists():
                return jsonify({'error': 'Project not found'}), 404

            if not project_dir.is_dir():
                return jsonify({'error': 'Project path is not a directory'}), 400

            # Stop the project if it's running
            if project_id in processes:
                logger.info(f"Stopping running project before deletion: {project_id}")
                process = processes[project_id]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                del processes[project_id]

            # Delete the project directory from _build/apps
            logger.info(f"Deleting project directory: {project_dir}")
            shutil.rmtree(project_dir)

            # Also delete associated setup extension and source files
            setup_ext_name = f"{project_id}_setup"

            # Remove from source/extensions/
            source_ext_dir = repo_root / "source" / "extensions" / setup_ext_name
            if source_ext_dir.exists():
                logger.info(f"Removing setup extension: {source_ext_dir}")
                shutil.rmtree(source_ext_dir)

            # Remove from source/apps/ (if it exists there)
            source_app_dir = repo_root / "source" / "apps" / project_id
            if source_app_dir.exists():
                logger.info(f"Removing source app: {source_app_dir}")
                shutil.rmtree(source_app_dir)

            # Remove from build directories (all platforms)
            build_dir = repo_root / "_build"
            if build_dir.exists():
                for platform_dir in build_dir.iterdir():
                    if not platform_dir.is_dir():
                        continue
                    for config_dir in platform_dir.iterdir():
                        if not config_dir.is_dir():
                            continue

                        # Remove .kit files and scripts
                        for pattern in [f"{project_id}.kit*", f"tests-{project_id}*"]:
                            for file in config_dir.glob(pattern):
                                if file.is_file():
                                    logger.info(f"Removing build artifact: {file}")
                                    file.unlink()

                        # Remove extensions
                        exts_dir = config_dir / "exts"
                        if exts_dir.exists():
                            for ext_name in [setup_ext_name, project_id]:
                                ext_path = exts_dir / ext_name
                                if ext_path.exists():
                                    logger.info(f"Removing built extension: {ext_path}")
                                    shutil.rmtree(ext_path)

            socketio.emit('log', {
                'level': 'info',
                'source': 'system',
                'message': f'Project and all associated files deleted: {project_id}'
            })

            return jsonify({'success': True})

        except Exception as e:
            logger.error(f"Failed to delete project: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return project_bp
