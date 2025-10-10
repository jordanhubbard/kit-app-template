#!/usr/bin/env python3
"""
Kit Playground Web Server
Flask-based REST API for template management, builds, and file operations

REFACTORED: Routes extracted into separate modules for better organization.
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import webbrowser
import time
import toml
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
from tools.repoman.repo_dispatcher import _fix_application_structure
from kit_playground.core.playground_app import PlaygroundApp
from kit_playground.backend.xpra_manager import XpraManager

# Import route blueprints
from kit_playground.backend.routes.template_routes import create_template_routes
from kit_playground.backend.routes.v2_template_routes import create_v2_template_routes
from kit_playground.backend.routes.project_routes import create_project_routes
from kit_playground.backend.routes.filesystem_routes import create_filesystem_routes
from kit_playground.backend.routes.xpra_routes import create_xpra_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaygroundWebServer:
    """Flask web server for Kit Playground."""

    def __init__(self, playground_app: PlaygroundApp, config):
        self.playground_app = playground_app
        self.config = config
        # Disable Flask's default static folder to avoid conflicts
        self.app = Flask(__name__, static_folder=None)
        CORS(self.app)  # Enable CORS for Electron renderer
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Running processes
        self.processes: Dict[str, subprocess.Popen] = {}

        # Initialize Xpra manager
        self.xpra_manager = XpraManager()

        # Track client IPs to log initial connections
        self.connected_clients = set()

        # Initialize unified Template API
        repo_root = Path(__file__).parent.parent.parent
        self.template_api = TemplateAPI(str(repo_root))

        # Setup routes and websocket
        self._setup_routes()
        self._setup_websocket()

    def _is_safe_project_name(self, name: str) -> bool:
        """Validate project name with basic safety checks.

        Args:
            name: Project name to validate

        Returns:
            True if the name is safe, False otherwise
        """
        # Allow alphanumeric, dots, hyphens, underscores, and spaces
        # Disallow dangerous shell metacharacters: ; & | $ ` ( ) < > \ " '
        if not name or len(name) > 255:
            return False

        # Check for dangerous characters
        dangerous_chars = [';', '&', '|', '$', '`', '(', ')', '<', '>', '\\', '"', "'", '\n', '\r', '\t']
        for char in dangerous_chars:
            if char in name:
                return False

        return True

    def _validate_project_path(self, repo_root: Path, project_path: str) -> Optional[Path]:
        """Validate and normalize project path to prevent path traversal.

        Args:
            repo_root: Repository root directory
            project_path: User-provided project path (relative)

        Returns:
            Validated absolute Path object or None if invalid
        """
        try:
            # Construct absolute path
            abs_path = (repo_root / project_path).resolve()

            # Ensure the path is within the repository
            repo_root_resolved = repo_root.resolve()
            if not str(abs_path).startswith(str(repo_root_resolved)):
                logger.warning(f"Path traversal attempt blocked: {project_path}")
                return None

            # Check path exists and is a directory
            if not abs_path.exists() or not abs_path.is_dir():
                logger.warning(f"Invalid project path (not a directory): {project_path}")
                return None

            return abs_path
        except Exception as e:
            logger.error(f"Error validating project path: {e}")
            return None

    def _validate_filesystem_path(self, path: str, allow_creation: bool = False) -> Optional[Path]:
        """Validate filesystem path with basic safety checks.

        Args:
            path: User-provided file/directory path (can be relative or absolute)
            allow_creation: If True, allow paths that don't exist yet

        Returns:
            Validated Path object or None if invalid
        """
        try:
            # Convert relative paths to absolute by resolving from repo root
            path_obj = Path(path)
            if not path_obj.is_absolute():
                repo_root = Path(__file__).parent.parent.parent
                path_obj = (repo_root / path).resolve()
            else:
                path_obj = path_obj.resolve()

            # Basic safety: prevent null bytes and other dangerous characters
            path_str = str(path_obj)
            if '\x00' in path_str:
                logger.warning(f"Filesystem access denied (null byte): {path}")
                return None

            # Ensure path is within repo root for security
            repo_root = Path(__file__).parent.parent.parent.resolve()
            try:
                path_obj.relative_to(repo_root)
            except ValueError:
                logger.warning(f"Filesystem access denied (outside repo): {path}")
                return None

            # If not allowing creation, check that path exists
            if not allow_creation and not path_obj.exists():
                return None

            return path_obj
        except Exception as e:
            logger.error(f"Error validating filesystem path: {e}")
            return None

    def _setup_routes(self):
        """Setup Flask routes by registering blueprints."""

        @self.app.before_request
        def log_connection():
            """Log incoming connections with timestamp and IP address."""
            # Get client IP address
            client_ip = request.remote_addr or 'unknown'

            # Log first connection from each IP
            if client_ip not in self.connected_clients:
                self.connected_clients.add(client_ip)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"New client connected from {client_ip} at {timestamp}")
                logger.info(f"Request: {request.method} {request.path}")

        # Register template routes
        template_bp = create_template_routes(self.playground_app, self.template_api)
        self.app.register_blueprint(template_bp)

        # Register v2 template routes with icon support
        v2_template_bp = create_v2_template_routes(
            self.playground_app,
            self.template_api,
            self.socketio  # Pass socketio for UI log emission
        )
        self.app.register_blueprint(v2_template_bp)

        # Register project routes
        project_bp = create_project_routes(
            self.playground_app,
            self.socketio,
            self.processes,
            self.xpra_manager,
            self  # Pass self for security validators
        )
        self.app.register_blueprint(project_bp)

        # Register filesystem routes
        filesystem_bp = create_filesystem_routes(self)  # Pass self for security validators
        self.app.register_blueprint(filesystem_bp)

        # Register Xpra routes
        xpra_bp = create_xpra_routes(self.xpra_manager)
        self.app.register_blueprint(xpra_bp)

        # Configuration routes (keep in main file as they're simple)
        @self.app.route('/api/config/paths', methods=['GET'])
        def get_default_paths():
            """Get default paths for templates and projects."""
            try:
                repo_root = Path(__file__).parent.parent.parent

                # Default paths relative to repo root
                templates_path = str(repo_root / 'templates')
                projects_path = str(repo_root / '_build' / 'apps')

                return jsonify({
                    'templatesPath': templates_path,
                    'projectsPath': projects_path,
                    'repoRoot': str(repo_root)
                })
            except Exception as e:
                logger.error(f"Failed to get default paths: {e}")
                return jsonify({'error': str(e)}), 500

        # Static file serving for UI
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def serve_ui(path):
            """Serve the React UI from the build directory."""
            ui_dir = Path(__file__).parent.parent / 'ui' / 'build'

            if path and (ui_dir / path).exists():
                return send_from_directory(str(ui_dir), path)
            else:
                return send_from_directory(str(ui_dir), 'index.html')

    def _setup_websocket(self):
        """Setup WebSocket event handlers."""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle client WebSocket connection."""
            client_id = request.sid
            logger.info(f"WebSocket client connected: {client_id}")
            emit('connection_response', {'data': 'Connected to Kit Playground'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client WebSocket disconnection."""
            client_id = request.sid
            logger.info(f"WebSocket client disconnected: {client_id}")

        @self.socketio.on('log')
        def handle_log(data):
            """Handle log messages from clients."""
            logger.info(f"Client log: {data}")

    def run(self, host: str = 'localhost', port: int = 8200, debug: bool = False):
        """
        Start the Flask web server.

        Args:
            host: Host address to bind to
            port: Port to listen on
            debug: Enable debug mode
        """
        logger.info(f"Starting Kit Playground web server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")

        # Use socketio.run instead of app.run for WebSocket support
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Disable reloader to prevent duplicate processes
            log_output=True
        )


def main():
    """Main entry point for standalone server."""
    import argparse

    parser = argparse.ArgumentParser(description='Kit Playground Web Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8200, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    # Create configuration
    from kit_playground.core.config import PlaygroundConfig
    config = PlaygroundConfig()

    # Create playground app
    app = PlaygroundApp(config)

    # Create and run web server
    server = PlaygroundWebServer(app, config)
    server.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
