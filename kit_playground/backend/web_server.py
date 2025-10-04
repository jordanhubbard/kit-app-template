#!/usr/bin/env python3
"""
Kit Playground Web Server
Flask-based REST API for template management, builds, and file operations
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import webbrowser
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.repoman.template_api import TemplateAPI, TemplateGenerationRequest
from tools.repoman.template_engine import TemplateEngine  # Legacy support
from kit_playground.core.playground_app import PlaygroundApp
from kit_playground.backend.xpra_manager import XpraManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaygroundWebServer:
    """Flask web server for Kit Playground."""

    def __init__(self, playground_app: PlaygroundApp, config):
        self.playground_app = playground_app
        self.config = config
        # Disable Flask's default static folder to avoid conflicts with our custom routing
        self.app = Flask(__name__, static_folder=None)
        CORS(self.app)  # Enable CORS for Electron renderer
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Running processes
        self.processes: Dict[str, subprocess.Popen] = {}

        # Track client IPs to log initial connections
        self.connected_clients = set()

        # Initialize unified Template API
        repo_root = Path(__file__).parent.parent.parent
        self.template_api = TemplateAPI(str(repo_root))

        # Initialize Xpra Manager
        self.xpra_manager = XpraManager()

        # Setup routes
        self._setup_routes()
        self._setup_websocket()

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.before_request
        def log_connection():
            """Log incoming connections with timestamp and IP address."""
            # Get client IP address
            client_ip = request.remote_addr
            if request.headers.get('X-Forwarded-For'):
                client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Log initial connection from new clients
            if client_ip not in self.connected_clients:
                self.connected_clients.add(client_ip)
                logger.info(f"[{timestamp}] Browser connected from {client_ip}")

            # Log all requests, but use different levels for API vs static files
            if request.path.startswith('/api/'):
                logger.info(f"[{timestamp}] Connection from {client_ip} - {request.method} {request.path}")
            else:
                # Log static file requests at debug level to reduce noise
                logger.debug(f"[{timestamp}] Connection from {client_ip} - {request.method} {request.path}")

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

        # Template routes
        @self.app.route('/api/templates', methods=['GET'])
        def get_templates():
            """Get all available templates."""
            try:
                templates = self.playground_app.get_all_templates()
                return jsonify(templates)
            except Exception as e:
                logger.error(f"Failed to get templates: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/templates/<template_id>/code', methods=['GET'])
        def get_template_code(template_id):
            """Get template information and description."""
            try:
                # Get template metadata
                templates = self.playground_app.get_all_templates()
                template = templates.get(template_id)

                if not template:
                    return jsonify({'error': 'Template not found'}), 404

                # Return template description as "code" for now
                # In a real implementation, this would generate sample code from the template
                description = f"""# {template.get('display_name', template_id)}

## Description
{template.get('description', 'No description available')}

## Type
{template.get('type', 'unknown')}

## Category
{template.get('category', 'unknown')}

## Usage
This is a template that can be used to generate new projects.
Click "Build" to generate a project from this template.

## Connectors
{chr(10).join(f"- {conn.get('name')}: {conn.get('type')} ({conn.get('direction')})" for conn in template.get('connectors', []))}
"""
                return description, 200, {'Content-Type': 'text/plain'}
            except Exception as e:
                logger.error(f"Failed to get template info: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/templates/<template_id>/update', methods=['POST'])
        def update_template_code(template_id):
            """Update template code."""
            try:
                data = request.json
                code = data.get('code', '')
                success = self.playground_app.update_template_code(template_id, code)

                if success:
                    return jsonify({'success': True})
                else:
                    return jsonify({'error': 'Failed to update code'}), 500
            except Exception as e:
                logger.error(f"Failed to update template code: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/templates/<template_id>/build', methods=['POST'])
        def build_template(template_id):
            """Build a template."""
            try:
                # Emit build status
                self.socketio.emit('log', {
                    'level': 'info',
                    'source': 'build',
                    'message': f'Building template: {template_id}'
                })

                # Run build in background thread
                def run_build():
                    asyncio.run(self._build_template_async(template_id))

                thread = threading.Thread(target=run_build)
                thread.start()

                return jsonify({'success': True, 'status': 'building'})
            except Exception as e:
                logger.error(f"Failed to start build: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/templates/<template_id>/run', methods=['POST'])
        def run_template(template_id):
            """Run a template."""
            try:
                asyncio.run(self._run_template_async(template_id))
                return jsonify({'success': True, 'previewUrl': f'http://localhost:8080/preview/{template_id}'})
            except Exception as e:
                logger.error(f"Failed to run template: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/templates/<template_id>/stop', methods=['POST'])
        def stop_template(template_id):
            """Stop a running template."""
            try:
                if template_id in self.processes:
                    self.processes[template_id].terminate()
                    del self.processes[template_id]
                    self.socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': f'Stopped template: {template_id}'
                    })
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Failed to stop template: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/templates/<template_id>/deploy', methods=['POST'])
        def deploy_template(template_id):
            """Deploy a template as standalone project."""
            try:
                data = request.json
                output_dir = data.get('outputPath')

                if not output_dir:
                    return jsonify({'error': 'outputPath required'}), 400

                # Generate standalone project
                playbook = self.playground_app.template_engine.generate_template(
                    template_name=template_id,
                    output_dir=output_dir
                )

                return jsonify({
                    'success': True,
                    'outputPath': output_dir,
                    'playbook': playbook
                })
            except Exception as e:
                logger.error(f"Failed to deploy template: {e}")
                return jsonify({'error': str(e)}), 500

        # Project routes
        @self.app.route('/api/projects', methods=['POST'])
        def create_project():
            """Create a new project."""
            try:
                data = request.json
                name = data.get('name', 'Untitled Project')
                output_path = data.get('outputPath', '')

                project = asyncio.run(self.playground_app.new_project(name))

                return jsonify({
                    'success': True,
                    'project': {
                        'id': project.id,
                        'name': project.name,
                        'outputPath': output_path
                    }
                })
            except Exception as e:
                logger.error(f"Failed to create project: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/projects/build', methods=['POST'])
        def build_project():
            """Build a Kit project using repo.sh."""
            try:
                data = request.json
                project_path = data.get('projectPath')
                project_name = data.get('projectName')

                if not project_path:
                    return jsonify({'error': 'projectPath required'}), 400

                # Run repo.sh build command
                repo_root = Path(__file__).parent.parent.parent
                result = subprocess.run(
                    [f'{repo_root}/repo.sh', 'build', '--path', project_path],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(repo_root)
                )

                # Emit build logs
                if result.stdout:
                    self.socketio.emit('log', {
                        'level': 'info',
                        'source': 'build',
                        'message': result.stdout
                    })

                if result.stderr:
                    self.socketio.emit('log', {
                        'level': 'error',
                        'source': 'build',
                        'message': result.stderr
                    })

                success = result.returncode == 0
                return jsonify({
                    'success': success,
                    'output': result.stdout,
                    'error': result.stderr if not success else None
                })
            except subprocess.TimeoutExpired:
                return jsonify({'error': 'Build timeout'}), 500
            except Exception as e:
                logger.error(f"Failed to build project: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/projects/run', methods=['POST'])
        def run_project():
            """Run a Kit project using repo.sh launch."""
            try:
                data = request.json
                project_path = data.get('projectPath')
                project_name = data.get('projectName')

                if not project_path:
                    return jsonify({'error': 'projectPath required'}), 400

                # Run repo.sh launch command in background
                repo_root = Path(__file__).parent.parent.parent
                process = subprocess.Popen(
                    [f'{repo_root}/repo.sh', 'launch', '--path', project_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=str(repo_root)
                )

                # Store process for later stop
                self.processes[project_name] = process

                self.socketio.emit('log', {
                    'level': 'info',
                    'source': 'runtime',
                    'message': f'Launched {project_name}'
                })

                return jsonify({
                    'success': True,
                    'message': 'Application launched',
                    'previewUrl': None  # TODO: Integrate with Xpra if available
                })
            except Exception as e:
                logger.error(f"Failed to run project: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/projects/stop', methods=['POST'])
        def stop_project():
            """Stop a running Kit project."""
            try:
                data = request.json
                project_name = data.get('projectName')

                if project_name in self.processes:
                    process = self.processes[project_name]
                    process.terminate()
                    del self.processes[project_name]

                    self.socketio.emit('log', {
                        'level': 'info',
                        'source': 'runtime',
                        'message': f'Stopped {project_name}'
                    })

                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Failed to stop project: {e}")
                return jsonify({'error': str(e)}), 500

        # ============= Unified Template API Routes =============
        # These routes use the shared template_api module for consistency between CLI and GUI

        @self.app.route('/api/v2/license/status', methods=['GET'])
        def get_license_status():
            """Get license acceptance status."""
            try:
                status = self.template_api.check_license()
                return jsonify({
                    'accepted': status.accepted,
                    'timestamp': status.timestamp,
                    'version': status.version
                })
            except Exception as e:
                logger.error(f"Failed to check license: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/v2/license/text', methods=['GET'])
        def get_license_text():
            """Get license text."""
            try:
                text = self.template_api.get_license_text()
                return jsonify({'text': text})
            except Exception as e:
                logger.error(f"Failed to get license text: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/v2/license/accept', methods=['POST'])
        def accept_license():
            """Accept license terms."""
            try:
                success = self.template_api.accept_license()
                return jsonify({'success': success})
            except Exception as e:
                logger.error(f"Failed to accept license: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/v2/templates', methods=['GET'])
        def list_templates_v2():
            """List templates using unified API."""
            try:
                template_type = request.args.get('type')
                category = request.args.get('category')
                templates = self.template_api.list_templates(template_type, category)

                # Convert to dict for JSON serialization
                result = []
                for t in templates:
                    result.append({
                        'id': t.name,
                        'name': t.name,
                        'displayName': t.display_name,
                        'type': t.type,
                        'category': t.category,
                        'description': t.description,
                        'version': t.version,
                        'tags': t.tags,
                        'documentation': t.documentation
                    })
                return jsonify(result)
            except Exception as e:
                logger.error(f"Failed to list templates: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/v2/templates/<template_id>/docs', methods=['GET'])
        def get_template_docs(template_id):
            """Get template documentation."""
            try:
                templates = self.template_api.list_templates()
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
                logger.error(f"Failed to get template docs: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/v2/templates/generate', methods=['POST'])
        def generate_template_v2():
            """Generate a template using unified API."""
            try:
                data = request.json
                req = TemplateGenerationRequest(
                    template_name=data.get('templateName'),
                    name=data.get('name'),
                    display_name=data.get('displayName'),
                    version=data.get('version', '0.1.0'),
                    config_file=data.get('configFile'),
                    output_dir=data.get('outputDir'),
                    add_layers=data.get('addLayers', False),
                    layers=data.get('layers'),
                    accept_license=data.get('acceptLicense', False),
                    extra_params=data.get('extraParams')
                )

                result = self.template_api.generate_template(req)

                if result.success:
                    return jsonify({
                        'success': True,
                        'playbackFile': result.playback_file,
                        'message': result.message,
                        'outputDir': req.output_dir or 'source/apps'
                    })
                else:
                    return jsonify({'success': False, 'error': result.error}), 400

            except Exception as e:
                logger.error(f"Failed to generate template: {e}")
                return jsonify({'error': str(e)}), 500

        # Xpra routes
        @self.app.route('/api/xpra/sessions', methods=['POST'])
        def create_xpra_session():
            """Create a new Xpra session."""
            try:
                data = request.json
                session_id = data.get('sessionId', f'session_{int(time.time())}')

                session = self.xpra_manager.create_session(session_id)
                if session:
                    return jsonify({
                        'success': True,
                        'sessionId': session_id,
                        'displayNumber': session.display_number,
                        'port': session.port,
                        'url': self.xpra_manager.get_session_url(session_id)
                    })
                else:
                    return jsonify({'error': 'Failed to create Xpra session'}), 500
            except Exception as e:
                logger.error(f"Failed to create Xpra session: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/xpra/sessions/<session_id>', methods=['GET'])
        def get_xpra_session(session_id):
            """Get Xpra session info."""
            try:
                session = self.xpra_manager.get_session(session_id)
                if session:
                    return jsonify({
                        'sessionId': session_id,
                        'displayNumber': session.display_number,
                        'port': session.port,
                        'url': self.xpra_manager.get_session_url(session_id),
                        'running': session.started
                    })
                else:
                    return jsonify({'error': 'Session not found'}), 404
            except Exception as e:
                logger.error(f"Failed to get Xpra session: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/xpra/sessions/<session_id>/launch', methods=['POST'])
        def launch_app_in_xpra(session_id):
            """Launch an application in an Xpra session."""
            try:
                data = request.json
                app_command = data.get('command')

                if not app_command:
                    return jsonify({'error': 'command required'}), 400

                session = self.xpra_manager.get_session(session_id)
                if not session:
                    return jsonify({'error': 'Session not found'}), 404

                success = session.launch_app(app_command)
                if success:
                    return jsonify({
                        'success': True,
                        'url': self.xpra_manager.get_session_url(session_id)
                    })
                else:
                    return jsonify({'error': 'Failed to launch app'}), 500
            except Exception as e:
                logger.error(f"Failed to launch app: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/xpra/sessions/<session_id>', methods=['DELETE'])
        def stop_xpra_session(session_id):
            """Stop an Xpra session."""
            try:
                self.xpra_manager.stop_session(session_id)
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Failed to stop Xpra session: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/xpra/check', methods=['GET'])
        def check_xpra_installed():
            """Check if Xpra is installed."""
            try:
                result = subprocess.run(['which', 'xpra'], capture_output=True)
                installed = result.returncode == 0

                version = None
                if installed:
                    version_result = subprocess.run(['xpra', '--version'],
                                                  capture_output=True, text=True)
                    if version_result.returncode == 0:
                        version = version_result.stdout.split()[1] if version_result.stdout else 'unknown'

                return jsonify({
                    'installed': installed,
                    'version': version,
                    'installCommand': 'make install-xpra'
                })
            except Exception as e:
                logger.error(f"Failed to check Xpra: {e}")
                return jsonify({'installed': False, 'error': str(e)})

        # Filesystem routes
        @self.app.route('/api/filesystem/cwd', methods=['GET'])
        def get_current_directory():
            """Get current working directory."""
            try:
                cwd = os.getcwd()
                return jsonify({
                    'cwd': cwd,
                    'realpath': str(Path(cwd).resolve())
                })
            except Exception as e:
                logger.error(f"Failed to get current directory: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/filesystem/list', methods=['GET'])
        def list_directory():
            """List directory contents."""
            try:
                path = request.args.get('path', str(Path.home()))
                path_obj = Path(path)

                if not path_obj.exists():
                    return jsonify({'error': 'Path does not exist'}), 404

                if not path_obj.is_dir():
                    return jsonify({'error': 'Path is not a directory'}), 400

                items = []
                for item in path_obj.iterdir():
                    try:
                        items.append({
                            'name': item.name,
                            'path': str(item),
                            'isDirectory': item.is_dir(),
                            'size': item.stat().st_size if item.is_file() else 0,
                            'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                    except (OSError, PermissionError):
                        continue  # Skip items we can't access

                return jsonify(items)
            except Exception as e:
                logger.error(f"Failed to list directory: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/filesystem/mkdir', methods=['POST'])
        def create_directory():
            """Create a new directory."""
            try:
                data = request.json
                path = data.get('path')

                if not path:
                    return jsonify({'error': 'path required'}), 400

                Path(path).mkdir(parents=True, exist_ok=True)
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Failed to create directory: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/filesystem/read', methods=['GET'])
        def read_file():
            """Read file contents."""
            try:
                path = request.args.get('path')

                if not path:
                    return jsonify({'error': 'path required'}), 400

                path_obj = Path(path)

                if not path_obj.exists():
                    return jsonify({'error': 'File does not exist'}), 404

                if not path_obj.is_file():
                    return jsonify({'error': 'Path is not a file'}), 400

                # Read file content
                content = path_obj.read_text(encoding='utf-8')
                return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
            except Exception as e:
                logger.error(f"Failed to read file: {e}")
                return jsonify({'error': str(e)}), 500

        # Configuration routes
        @self.app.route('/api/config/paths', methods=['GET'])
        def get_default_paths():
            """Get default paths for templates and projects."""
            try:
                repo_root = Path(__file__).parent.parent.parent

                # Default paths relative to repo root
                templates_path = str(repo_root / 'templates')
                projects_path = str(repo_root / 'source' / 'apps')

                return jsonify({
                    'templatesPath': templates_path,
                    'projectsPath': projects_path,
                    'repoRoot': str(repo_root)
                })
            except Exception as e:
                logger.error(f"Failed to get default paths: {e}")
                return jsonify({'error': str(e)}), 500

        # Project discovery routes
        @self.app.route('/api/projects/discover', methods=['GET'])
        def discover_projects():
            """Discover projects in a directory."""
            try:
                projects_path = request.args.get('path', str(Path(__file__).parent.parent.parent / 'source' / 'apps'))
                projects_dir = Path(projects_path)

                if not projects_dir.exists():
                    return jsonify({'projects': []})

                projects = []

                # Look for .kit directories (each project is a .kit directory)
                for item in projects_dir.iterdir():
                    if item.is_dir() and item.suffix == '.kit':
                        project_name = item.stem
                        kit_file = item / f"{project_name}.kit"

                        # Check if .kit file exists
                        if kit_file.exists():
                            # Try to read project metadata from .kit file
                            try:
                                # Basic project info
                                project_info = {
                                    'id': project_name,
                                    'name': project_name,
                                    'displayName': project_name.replace('_', ' ').title(),
                                    'path': str(item),
                                    'kitFile': str(kit_file),
                                    'status': 'ready',  # TODO: Detect if built/running
                                    'lastModified': item.stat().st_mtime
                                }
                                projects.append(project_info)
                            except Exception as e:
                                logger.warning(f"Failed to read project {project_name}: {e}")

                # Sort by last modified (newest first)
                projects.sort(key=lambda p: p['lastModified'], reverse=True)

                return jsonify({'projects': projects})
            except Exception as e:
                logger.error(f"Failed to discover projects: {e}")
                return jsonify({'error': str(e)}), 500

        # Serve static React build files (catch-all, must be last)
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def serve_static(path):
            """Serve static files from React build directory."""
            static_dir = Path(__file__).parent.parent / 'ui' / 'build'

            # API routes are handled above, so this won't interfere
            if path.startswith('api/'):
                return jsonify({'error': 'API endpoint not found'}), 404

            if path and (static_dir / path).exists():
                # Use absolute path to ensure correct file serving
                return send_from_directory(str(static_dir), path)
            else:
                # For React Router - serve index.html for all routes
                return send_from_directory(str(static_dir), 'index.html')

    def _setup_websocket(self):
        """Setup WebSocket handlers for streaming logs."""

        @self.socketio.on('connect')
        def handle_connect():
            logger.info('Client connected to WebSocket')
            emit('connected', {'status': 'ok'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info('Client disconnected from WebSocket')

    async def _build_template_async(self, template_id: str):
        """Build template asynchronously."""
        try:
            self.socketio.emit('log', {
                'level': 'info',
                'source': 'build',
                'message': f'Starting build for {template_id}...'
            })

            # Use playground app to build
            if not self.playground_app.current_project:
                await self.playground_app.new_project(f'temp_{template_id}')
                await self.playground_app.add_template_to_project(template_id)

            success = await self.playground_app.build_project()

            if success:
                self.socketio.emit('log', {
                    'level': 'success',
                    'source': 'build',
                    'message': f'Build completed successfully!'
                })
            else:
                self.socketio.emit('log', {
                    'level': 'error',
                    'source': 'build',
                    'message': f'Build failed!'
                })

        except Exception as e:
            logger.error(f"Build error: {e}")
            self.socketio.emit('log', {
                'level': 'error',
                'source': 'build',
                'message': f'Build error: {str(e)}'
            })

    async def _run_template_async(self, template_id: str):
        """Run template asynchronously."""
        try:
            self.socketio.emit('log', {
                'level': 'info',
                'source': 'runtime',
                'message': f'Starting {template_id}...'
            })

            success = await self.playground_app.run_project()

            if success:
                self.socketio.emit('log', {
                    'level': 'success',
                    'source': 'runtime',
                    'message': f'Template running!'
                })
        except Exception as e:
            logger.error(f"Run error: {e}")
            self.socketio.emit('log', {
                'level': 'error',
                'source': 'runtime',
                'message': f'Run error: {str(e)}'
            })

    def start(self, host: str = 'localhost', port: int = 8200, open_browser: bool = False):
        """Start the web server."""
        # Try to find an available port if the specified port is in use
        original_port = port
        max_attempts = 10

        for attempt in range(max_attempts):
            try:
                # Test if port is available
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((host, port))
                sock.close()

                # Port is available
                if port != original_port:
                    logger.warning(f"Port {original_port} is in use, using port {port} instead")

                logger.info(f"Starting Kit Playground Web Server on {host}:{port}")

                # Open browser after server starts
                if open_browser:
                    def open_browser_delayed():
                        time.sleep(1.5)  # Wait for server to start
                        url = f"http://{host}:{port}"
                        logger.info(f"Opening browser at {url}")
                        webbrowser.open(url)

                    threading.Thread(target=open_browser_delayed, daemon=True).start()

                self.socketio.run(self.app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
                return

            except OSError as e:
                if attempt < max_attempts - 1:
                    port += 1
                    continue
                else:
                    logger.error(f"Failed to find an available port after {max_attempts} attempts")
                    raise

    def stop(self):
        """Stop the web server."""
        # Cleanup running processes
        for process in self.processes.values():
            try:
                process.terminate()
            except:
                pass

        # Stop all Xpra sessions
        self.xpra_manager.stop_all()

        logger.info("Kit Playground Web Server stopped")


if __name__ == '__main__':
    # Standalone mode
    import argparse
    parser = argparse.ArgumentParser(description='Kit Playground Web Server')
    parser.add_argument('--port', type=int, default=8200, help='Server port (default: 8200)')
    parser.add_argument('--host', default='localhost', help='Server host (use 0.0.0.0 for remote access)')
    parser.add_argument('--open-browser', action='store_true', help='Automatically open browser')
    args = parser.parse_args()

    # Check for X server on Linux
    if sys.platform.startswith('linux'):
        if not os.environ.get('DISPLAY'):
            logger.warning("DISPLAY environment variable not set!")
            logger.warning("Kit applications may not be able to display windows.")
            logger.warning("If using SSH, connect with: ssh -X user@host")

    # Check if React build exists
    build_dir = Path(__file__).parent.parent / 'ui' / 'build'
    if not build_dir.exists():
        logger.error("React build not found!")
        logger.error(f"Expected build directory: {build_dir}")
        logger.error("Please run: cd kit_playground/ui && npm install && npm run build")
        sys.exit(1)

    # Create playground app
    class Config:
        def get(self, key, default=None):
            return default

    config = Config()
    repo_root = Path(__file__).parent.parent.parent
    template_engine = TemplateEngine(str(repo_root))

    from kit_playground.core.playground_app import PlaygroundApp
    app = PlaygroundApp(config)

    # Create and start server (blocking call)
    server = PlaygroundWebServer(app, config)
    logger.info(f"Kit Playground UI available at: http://{args.host}:{args.port}")
    server.start(args.host, args.port, open_browser=args.open_browser)