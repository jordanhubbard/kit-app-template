#!/usr/bin/env python3
"""
Core application logic for Kit Playground.
Manages templates, connections, and project lifecycle.
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Import connector system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.repoman.connector_system import (
    ConnectorGraph,
    ConnectorResolver,
    load_template_connector_spec,
    TemplateNode,
    Connector,
    DataRequirement
)
from tools.repoman.template_engine import TemplateEngine

logger = logging.getLogger(__name__)


@dataclass
class PlaygroundProject:
    """Represents a project in Kit Playground."""
    id: str
    name: str
    created_at: datetime
    modified_at: datetime
    templates: List[str] = field(default_factory=list)
    connections: List[Tuple[str, str, str, str]] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    build_output: Optional[str] = None
    is_built: bool = False
    is_running: bool = False
    process: Optional[subprocess.Popen] = None


class PlaygroundApp:
    """Main application class for Kit Playground."""

    def __init__(self, config):
        self.config = config
        self.repo_root = Path(__file__).parent.parent.parent
        self.template_engine = TemplateEngine(str(self.repo_root))
        self.connector_graph = ConnectorGraph()
        self.connector_resolver = ConnectorResolver(self.connector_graph)
        self.current_project: Optional[PlaygroundProject] = None
        self.projects: Dict[str, PlaygroundProject] = {}
        self.server = None
        self.ui_app = None

        # Load all templates and their connectors
        self._load_templates()

    def _load_templates(self):
        """Load all available templates and their connector specifications."""
        templates = self.template_engine.template_discovery.discover_templates()

        for name, template_config in templates.items():
            try:
                template_node = load_template_connector_spec(template_config)
                self.connector_graph.add_template(name, template_node.connectors)
                logger.info(f"Loaded template: {name}")
            except Exception as e:
                logger.error(f"Failed to load template {name}: {e}")

    async def new_project(self, name: str) -> PlaygroundProject:
        """Create a new project."""
        project_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project = PlaygroundProject(
            id=project_id,
            name=name,
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        self.projects[project_id] = project
        self.current_project = project
        logger.info(f"Created new project: {name}")
        return project

    async def new_project_from_template(self, template_name: str) -> PlaygroundProject:
        """Create a new project starting with a template."""
        project = await self.new_project(f"project_{template_name}")
        await self.add_template_to_project(template_name)
        return project

    async def load_project(self, project_path: str) -> PlaygroundProject:
        """Load an existing project."""
        path = Path(project_path)
        if not path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")

        with open(path / "playground_project.json", 'r') as f:
            data = json.load(f)

        project = PlaygroundProject(
            id=data['id'],
            name=data['name'],
            created_at=datetime.fromisoformat(data['created_at']),
            modified_at=datetime.fromisoformat(data['modified_at']),
            templates=data['templates'],
            connections=data['connections'],
            configuration=data['configuration']
        )

        self.projects[project.id] = project
        self.current_project = project
        logger.info(f"Loaded project: {project.name}")
        return project

    async def save_project(self, project_path: Optional[str] = None):
        """Save the current project."""
        if not self.current_project:
            raise ValueError("No active project to save")

        if not project_path:
            project_path = Path.home() / '.kit_playground' / 'projects' / self.current_project.id

        path = Path(project_path)
        path.mkdir(parents=True, exist_ok=True)

        data = {
            'id': self.current_project.id,
            'name': self.current_project.name,
            'created_at': self.current_project.created_at.isoformat(),
            'modified_at': datetime.now().isoformat(),
            'templates': self.current_project.templates,
            'connections': self.current_project.connections,
            'configuration': self.current_project.configuration
        }

        with open(path / "playground_project.json", 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved project to: {path}")

    async def add_template_to_project(self, template_name: str, config: Optional[Dict[str, Any]] = None):
        """Add a template to the current project."""
        if not self.current_project:
            raise ValueError("No active project")

        if template_name not in self.connector_graph.nodes:
            raise ValueError(f"Unknown template: {template_name}")

        self.current_project.templates.append(template_name)

        if config:
            self.current_project.configuration[template_name] = config

        # Check for missing requirements
        node = self.connector_graph.nodes[template_name]
        missing = node.get_missing_requirements(
            self.current_project.configuration.get(template_name, {})
        )

        if missing:
            logger.warning(f"Template {template_name} has missing requirements: {[r.name for r in missing]}")
            # In UI mode, this would trigger prompts for the user

        logger.info(f"Added template {template_name} to project")

    async def connect_templates(self, from_template: str, from_connector: str,
                               to_template: str, to_connector: str):
        """Connect two templates in the current project."""
        if not self.current_project:
            raise ValueError("No active project")

        # Validate connection
        can_connect, error = self.connector_graph.can_connect(
            from_template, to_template, from_connector, to_connector
        )

        if not can_connect:
            raise ValueError(f"Cannot connect: {error}")

        # Add connection
        self.connector_graph.connect(from_template, to_template, from_connector, to_connector)
        self.current_project.connections.append(
            (from_template, from_connector, to_template, to_connector)
        )

        logger.info(f"Connected {from_template}.{from_connector} to {to_template}.{to_connector}")

    async def auto_connect_templates(self):
        """Automatically connect compatible templates in the project."""
        if not self.current_project:
            raise ValueError("No active project")

        connections = self.connector_resolver.auto_connect(self.current_project.templates)

        for conn in connections:
            await self.connect_templates(*conn)

        logger.info(f"Auto-connected {len(connections)} template pairs")
        return connections

    async def validate_project(self) -> Tuple[bool, List[str]]:
        """Validate the current project configuration."""
        if not self.current_project:
            raise ValueError("No active project")

        return self.connector_graph.validate_configuration(self.current_project.templates)

    async def build_project(self) -> bool:
        """Build the current project."""
        if not self.current_project:
            raise ValueError("No active project")

        # Validate first
        valid, errors = await self.validate_project()
        if not valid:
            logger.error(f"Project validation failed: {errors}")
            return False

        # Create temporary output directory
        output_dir = Path.home() / '.kit_playground' / 'builds' / self.current_project.id
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Generate project files for each template
            for template_name in self.current_project.templates:
                config = self.current_project.configuration.get(template_name, {})

                # Use template engine to generate files
                playbook = self.template_engine.generate_template(
                    template_name=template_name,
                    output_dir=str(output_dir / template_name),
                    **config
                )

            # Run build command
            build_cmd = [str(self.repo_root / "repo.sh"), "build"]
            result = subprocess.run(
                build_cmd,
                cwd=str(output_dir),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.current_project.is_built = True
                self.current_project.build_output = str(output_dir)
                logger.info("Project built successfully")
                return True
            else:
                logger.error(f"Build failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Build error: {e}")
            return False

    async def run_project(self) -> bool:
        """Run the current project."""
        if not self.current_project:
            raise ValueError("No active project")

        if not self.current_project.is_built:
            logger.warning("Project not built, building now...")
            if not await self.build_project():
                return False

        try:
            # Run the application
            run_cmd = [str(self.repo_root / "repo.sh"), "launch"]
            self.current_project.process = subprocess.Popen(
                run_cmd,
                cwd=self.current_project.build_output,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.current_project.is_running = True
            logger.info("Project is running")
            return True

        except Exception as e:
            logger.error(f"Run error: {e}")
            return False

    async def stop_project(self):
        """Stop the running project."""
        if not self.current_project or not self.current_project.is_running:
            return

        if self.current_project.process:
            self.current_project.process.terminate()
            self.current_project.process = None

        self.current_project.is_running = False
        logger.info("Project stopped")

    async def get_template_suggestions(self, template_name: str) -> Dict[str, List[str]]:
        """Get connection suggestions for a template."""
        return self.connector_resolver.suggest_connections(template_name)

    async def resolve_requirements(self, template_name: str,
                                  user_data: Dict[str, str]) -> Tuple[bool, List[DataRequirement]]:
        """Resolve data requirements for a template."""
        return self.connector_resolver.resolve_requirements(template_name, user_data)

    # UI Mode Starters
    async def start_web_mode(self, open_browser: bool = True):
        """Start Kit Playground in web mode."""
        from kit_playground.backend.web_server import PlaygroundWebServer

        self.server = PlaygroundWebServer(self, self.config)

        port = self.config.get('server.port', 8080)
        host = self.config.get('server.host', 'localhost')

        logger.info(f"Kit Playground Web UI running at http://{host}:{port}")

        # Start the web server (blocking call - it runs in the current thread)
        # The web server's start() method is synchronous and blocks
        self.server.start(host, port, open_browser=open_browser)

    async def start_native_mode(self):
        """Start Kit Playground in native mode with Qt."""
        try:
            from kit_playground.frontend.native.main_window import PlaygroundMainWindow
            from PySide6.QtWidgets import QApplication
            import sys

            app = QApplication(sys.argv)
            self.ui_app = PlaygroundMainWindow(self)
            self.ui_app.show()

            logger.info("Kit Playground Native UI started")
            sys.exit(app.exec())

        except ImportError:
            logger.error("Native UI requires PySide6. Install with: pip install PySide6")
            raise

    async def start_headless_mode(self):
        """Start Kit Playground in headless mode (API only)."""
        from kit_playground.backend.api_server import PlaygroundAPIServer

        self.server = PlaygroundAPIServer(self, self.config)

        port = self.config.get('server.port', 8080)
        host = self.config.get('server.host', 'localhost')

        logger.info(f"Kit Playground API running at http://{host}:{port}")

        # Start the API server (blocking call)
        self.server.start(host, port)

    # Template Gallery Methods
    def get_all_templates(self) -> Dict[str, Any]:
        """Get all available templates with metadata."""
        templates = {}

        for name, template_config in self.template_engine.template_discovery.discover_templates().items():
            metadata = template_config.get('metadata', {})
            visual = metadata.get('visual', {})

            templates[name] = {
                'name': name,
                'display_name': metadata.get('display_name', name),
                'type': metadata.get('type', 'unknown'),
                'category': metadata.get('category', 'general'),
                'description': metadata.get('description', ''),
                'thumbnail': visual.get('thumbnail'),
                'icon': visual.get('icon'),
                'color_scheme': visual.get('color_scheme'),
                'connectors': self._get_template_connectors(name)
            }

        return templates

    def _get_template_connectors(self, template_name: str) -> List[Dict[str, Any]]:
        """Get connector information for a template."""
        if template_name not in self.connector_graph.nodes:
            return []

        node = self.connector_graph.nodes[template_name]
        connectors = []

        for conn in node.connectors:
            connectors.append({
                'name': conn.name,
                'type': conn.connector_type.value,
                'protocol': conn.protocol.value,
                'direction': conn.direction.value,
                'required': conn.required,
                'description': conn.description
            })

        return connectors

    def get_template_code(self, template_name: str) -> Optional[str]:
        """Get the source code for a template."""
        template_config = self.template_engine.template_discovery.get_template(template_name)
        if not template_config:
            return None

        # Get the template source directory
        template_dir = Path(template_config.get('_template_dir', ''))
        source_dir = template_config.get('template', {}).get('source_dir')

        if source_dir:
            source_path = self.repo_root / "templates" / source_dir
            # Read main file (this would be customizable per template)
            main_files = list(source_path.glob("**/*.py")) + list(source_path.glob("**/*.kit"))

            if main_files:
                with open(main_files[0], 'r') as f:
                    return f.read()

        return None

    def update_template_code(self, template_name: str, code: str) -> bool:
        """Update the code for a template in the current project."""
        if not self.current_project:
            return False

        # Store customized code in project configuration
        if 'custom_code' not in self.current_project.configuration:
            self.current_project.configuration['custom_code'] = {}

        self.current_project.configuration['custom_code'][template_name] = code
        self.current_project.modified_at = datetime.now()

        return True