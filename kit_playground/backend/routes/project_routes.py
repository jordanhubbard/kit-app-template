"""
Project build and run routes for Kit Playground.
"""
import logging
import subprocess
import threading
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
                    'error': 'Invalid project name. Use only alphanumeric characters, dots, hyphens, and underscores.'
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
                    'error': 'Invalid project name. Use only alphanumeric characters, dots, hyphens, and underscores.'
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

    @project_bp.route('/stop/<project_name>', methods=['POST'])
    def stop_project(project_name: str):
        """Stop a running project."""
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

    return project_bp

