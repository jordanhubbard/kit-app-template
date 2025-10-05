#!/usr/bin/env python3
"""
Connector System for Kit App Template
Manages inter-template communication, data flow, and dependency resolution.
"""

import base64
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from io import BytesIO

# Try to import PIL for image processing
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ConnectorDirection(Enum):
    """Direction of data flow for a connector."""
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"


class ConnectorType(Enum):
    """Types of connectors available."""
    DATA_SOURCE = "data_source"
    DATA_SINK = "data_sink"
    CONFIGURATION = "configuration"
    COMMUNICATION = "communication"
    COMPUTE = "compute"
    UI_COMPONENT = "ui_component"


class ConnectorProtocol(Enum):
    """Supported communication protocols."""
    OMNIVERSE = "omniverse"
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    FILE = "file"
    STREAMING = "streaming"
    JSON = "json"
    GRAPHQL = "graphql"


@dataclass
class Connector:
    """Represents a single connector specification."""
    name: str
    connector_type: ConnectorType
    protocol: ConnectorProtocol
    direction: ConnectorDirection
    required: bool = False
    description: str = ""
    mime_types: List[str] = field(default_factory=list)
    schema: Optional[str] = None
    compatible_with: List[str] = field(default_factory=list)

    def is_compatible_with(self, other: 'Connector') -> bool:
        """Check if this connector is compatible with another."""
        # Check protocol compatibility
        if self.protocol != other.protocol:
            return False

        # Check direction compatibility
        if self.direction == ConnectorDirection.INPUT and other.direction == ConnectorDirection.OUTPUT:
            return True
        elif self.direction == ConnectorDirection.OUTPUT and other.direction == ConnectorDirection.INPUT:
            return True
        elif self.direction == ConnectorDirection.BIDIRECTIONAL and other.direction == ConnectorDirection.BIDIRECTIONAL:
            return True

        return False

    def matches_mime_types(self, mime_type: str) -> bool:
        """Check if a MIME type is supported by this connector."""
        if not self.mime_types:
            return True  # No restrictions
        return mime_type in self.mime_types


@dataclass
class ConnectorRule:
    """Defines interaction rules between templates."""
    rule_type: str  # allows, requires, provides, excludes
    template: str
    connector: Optional[str] = None
    mode: Optional[str] = None
    description: str = ""
    reason: Optional[str] = None


@dataclass
class DataRequirement:
    """Represents a data requirement that may need user input."""
    id: str
    name: str
    requirement_type: str  # file_path, directory_path, service_endpoint, secure_string
    required: bool = True
    prompt: str = ""
    default: Optional[str] = None
    validation: Optional[str] = None
    mime_types: List[str] = field(default_factory=list)

    def validate_input(self, value: str) -> Tuple[bool, Optional[str]]:
        """Validate user input against requirement rules."""
        if self.required and not value:
            return False, f"{self.name} is required"

        if not value:
            return True, None

        if self.validation:
            if self.validation == "file_exists":
                if not Path(value).exists():
                    return False, f"File does not exist: {value}"
            elif self.validation == "url_reachable":
                # TODO: Implement URL validation
                pass
            elif self.validation.startswith("regex:"):
                pattern = self.validation[6:]
                if not re.match(pattern, value):
                    return False, f"Invalid format for {self.name}"

        return True, None


@dataclass
class TemplateVisual:
    """Visual representation of a template."""
    thumbnail: Optional[str] = None  # Base64 encoded image
    icon: Optional[str] = None  # Icon name
    color_scheme: Optional[str] = None  # Hex color

    def get_thumbnail_image(self) -> Optional[bytes]:
        """Decode and return thumbnail image data."""
        if not self.thumbnail:
            return None

        if self.thumbnail.startswith("data:image/"):
            # Extract base64 data
            header, data = self.thumbnail.split(",", 1)
            return base64.b64decode(data)

        return None

    def generate_default_thumbnail(self, template_type: str) -> str:
        """Generate a default thumbnail based on template type."""
        if not HAS_PIL:
            return ""

        # Create a simple colored square with text
        img = Image.new('RGB', (256, 256), color=self._get_color_for_type(template_type))

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_data = buffer.getvalue()

        return f"data:image/png;base64,{base64.b64encode(img_data).decode()}"

    def _get_color_for_type(self, template_type: str) -> tuple:
        """Get a color for the template type."""
        colors = {
            "application": (76, 175, 80),    # Green
            "extension": (33, 150, 243),     # Blue
            "microservice": (255, 152, 0),   # Orange
            "component": (156, 39, 176)      # Purple
        }
        return colors.get(template_type, (158, 158, 158))  # Default gray


class ConnectorGraph:
    """Manages the connection graph between templates."""

    def __init__(self):
        self.nodes: Dict[str, 'TemplateNode'] = {}
        self.edges: List[Tuple[str, str, Connector]] = []

    def add_template(self, template_name: str, connectors: List[Connector]):
        """Add a template node to the graph."""
        self.nodes[template_name] = TemplateNode(template_name, connectors)

    def can_connect(self, from_template: str, to_template: str,
                    from_connector: str, to_connector: str) -> Tuple[bool, Optional[str]]:
        """Check if two templates can be connected via specified connectors."""
        if from_template not in self.nodes:
            return False, f"Template {from_template} not found"
        if to_template not in self.nodes:
            return False, f"Template {to_template} not found"

        from_node = self.nodes[from_template]
        to_node = self.nodes[to_template]

        from_conn = from_node.get_connector(from_connector)
        to_conn = to_node.get_connector(to_connector)

        if not from_conn:
            return False, f"Connector {from_connector} not found in {from_template}"
        if not to_conn:
            return False, f"Connector {to_connector} not found in {to_template}"

        if not from_conn.is_compatible_with(to_conn):
            return False, "Connectors are not compatible"

        # Check for circular dependencies
        if self._would_create_cycle(from_template, to_template):
            return False, "Connection would create a circular dependency"

        return True, None

    def connect(self, from_template: str, to_template: str,
                from_connector: str, to_connector: str) -> bool:
        """Create a connection between two templates."""
        can_connect, error = self.can_connect(from_template, to_template,
                                             from_connector, to_connector)
        if not can_connect:
            raise ValueError(error)

        from_conn = self.nodes[from_template].get_connector(from_connector)
        self.edges.append((from_template, to_template, from_conn))
        return True

    def _would_create_cycle(self, from_template: str, to_template: str) -> bool:
        """Check if adding an edge would create a cycle."""
        # Simple DFS cycle detection
        visited = set()

        def has_path(start: str, end: str) -> bool:
            if start == end:
                return True
            if start in visited:
                return False
            visited.add(start)

            for edge in self.edges:
                if edge[0] == start:
                    if has_path(edge[1], end):
                        return True
            return False

        # Check if there's already a path from to_template to from_template
        return has_path(to_template, from_template)

    def get_required_templates(self, template_name: str) -> Set[str]:
        """Get all templates required by the given template."""
        required = set()
        if template_name not in self.nodes:
            return required

        node = self.nodes[template_name]
        for connector in node.connectors:
            if connector.required and connector.direction == ConnectorDirection.INPUT:
                # Find templates that can provide this input
                for other_name, other_node in self.nodes.items():
                    if other_name == template_name:
                        continue
                    for other_conn in other_node.connectors:
                        if connector.is_compatible_with(other_conn):
                            required.add(other_name)

        return required

    def validate_configuration(self, selected_templates: List[str]) -> Tuple[bool, List[str]]:
        """Validate that all required connections can be satisfied."""
        errors = []

        for template in selected_templates:
            if template not in self.nodes:
                errors.append(f"Unknown template: {template}")
                continue

            node = self.nodes[template]
            for connector in node.connectors:
                if connector.required and connector.direction == ConnectorDirection.INPUT:
                    # Check if any selected template can provide this input
                    found_provider = False
                    for other_template in selected_templates:
                        if other_template == template:
                            continue
                        if other_template in self.nodes:
                            other_node = self.nodes[other_template]
                            for other_conn in other_node.connectors:
                                if connector.is_compatible_with(other_conn):
                                    found_provider = True
                                    break
                        if found_provider:
                            break

                    if not found_provider:
                        errors.append(
                            f"{template} requires {connector.name} ({connector.connector_type.value}) "
                            f"but no provider is available"
                        )

        return len(errors) == 0, errors


@dataclass
class TemplateNode:
    """Represents a template in the connector graph."""
    name: str
    connectors: List[Connector]
    rules: List[ConnectorRule] = field(default_factory=list)
    requirements: List[DataRequirement] = field(default_factory=list)
    visual: Optional[TemplateVisual] = None

    def get_connector(self, name: str) -> Optional[Connector]:
        """Get a connector by name."""
        for conn in self.connectors:
            if conn.name == name:
                return conn
        return None

    def get_inputs(self) -> List[Connector]:
        """Get all input connectors."""
        return [c for c in self.connectors
                if c.direction in [ConnectorDirection.INPUT, ConnectorDirection.BIDIRECTIONAL]]

    def get_outputs(self) -> List[Connector]:
        """Get all output connectors."""
        return [c for c in self.connectors
                if c.direction in [ConnectorDirection.OUTPUT, ConnectorDirection.BIDIRECTIONAL]]

    def is_compatible_with(self, other: 'TemplateNode') -> bool:
        """Check if this template can connect to another."""
        for our_conn in self.connectors:
            for their_conn in other.connectors:
                if our_conn.is_compatible_with(their_conn):
                    return True
        return False

    def get_missing_requirements(self, provided_data: Dict[str, str]) -> List[DataRequirement]:
        """Get requirements that haven't been provided."""
        missing = []
        for req in self.requirements:
            if req.required and req.id not in provided_data:
                missing.append(req)
        return missing


class ConnectorResolver:
    """Resolves data requirements and missing connections."""

    def __init__(self, graph: ConnectorGraph):
        self.graph = graph

    def resolve_requirements(self, template_name: str,
                            user_data: Dict[str, str]) -> Tuple[bool, List[DataRequirement]]:
        """Resolve data requirements for a template."""
        if template_name not in self.graph.nodes:
            return False, []

        node = self.graph.nodes[template_name]
        missing = node.get_missing_requirements(user_data)

        return len(missing) == 0, missing

    def suggest_connections(self, template_name: str) -> Dict[str, List[str]]:
        """Suggest compatible templates for each connector."""
        suggestions = {}

        if template_name not in self.graph.nodes:
            return suggestions

        node = self.graph.nodes[template_name]

        for connector in node.connectors:
            compatible = []
            for other_name, other_node in self.graph.nodes.items():
                if other_name == template_name:
                    continue

                for other_conn in other_node.connectors:
                    if connector.is_compatible_with(other_conn):
                        compatible.append(f"{other_name}.{other_conn.name}")
                        break

            if compatible:
                suggestions[connector.name] = compatible

        return suggestions

    def auto_connect(self, templates: List[str]) -> List[Tuple[str, str, str, str]]:
        """Automatically connect compatible templates."""
        connections = []

        for i, template1 in enumerate(templates):
            if template1 not in self.graph.nodes:
                continue

            node1 = self.graph.nodes[template1]

            for j, template2 in enumerate(templates[i+1:], i+1):
                if template2 not in self.graph.nodes:
                    continue

                node2 = self.graph.nodes[template2]

                # Find compatible connectors
                for conn1 in node1.connectors:
                    for conn2 in node2.connectors:
                        if conn1.is_compatible_with(conn2):
                            connections.append(
                                (template1, conn1.name, template2, conn2.name)
                            )
                            break

        return connections


def load_template_connector_spec(template_config: Dict[str, Any]) -> TemplateNode:
    """Load connector specifications from a template configuration."""
    name = template_config.get('metadata', {}).get('name', 'unknown')

    # Parse connectors
    connectors = []
    connector_specs = template_config.get('connectors', {})

    for conn_type in ['inputs', 'outputs', 'bidirectional']:
        for conn_spec in connector_specs.get(conn_type, []):
            direction = ConnectorDirection.BIDIRECTIONAL if conn_type == 'bidirectional' else \
                       ConnectorDirection.INPUT if conn_type == 'inputs' else \
                       ConnectorDirection.OUTPUT

            connector = Connector(
                name=conn_spec.get('name', ''),
                connector_type=ConnectorType(conn_spec.get('type', 'data_source')),
                protocol=ConnectorProtocol(conn_spec.get('protocol', 'json')),
                direction=direction,
                required=conn_spec.get('required', False),
                description=conn_spec.get('description', ''),
                mime_types=conn_spec.get('mime_types', []),
                schema=conn_spec.get('schema'),
                compatible_with=conn_spec.get('compatible_with', [])
            )
            connectors.append(connector)

    # Parse rules
    rules = []
    rule_specs = template_config.get('connector_rules', {})

    for rule_type in ['allows', 'requires', 'provides', 'excludes']:
        for rule_spec in rule_specs.get(rule_type, []):
            rule = ConnectorRule(
                rule_type=rule_type,
                template=rule_spec.get('template', ''),
                connector=rule_spec.get('connector'),
                mode=rule_spec.get('mode'),
                description=rule_spec.get('description', ''),
                reason=rule_spec.get('reason')
            )
            rules.append(rule)

    # Parse requirements
    requirements = []
    req_specs = template_config.get('requirements', {})

    for req_type in ['data_sources', 'services', 'credentials']:
        for req_spec in req_specs.get(req_type, []):
            requirement = DataRequirement(
                id=req_spec.get('id', ''),
                name=req_spec.get('name', ''),
                requirement_type=req_spec.get('type', 'file_path'),
                required=req_spec.get('required', True),
                prompt=req_spec.get('prompt', ''),
                default=req_spec.get('default'),
                validation=req_spec.get('validation'),
                mime_types=req_spec.get('mime_types', [])
            )
            requirements.append(requirement)

    # Parse visual
    visual_spec = template_config.get('metadata', {}).get('visual', {})
    visual = TemplateVisual(
        thumbnail=visual_spec.get('thumbnail'),
        icon=visual_spec.get('icon'),
        color_scheme=visual_spec.get('color_scheme')
    )

    return TemplateNode(
        name=name,
        connectors=connectors,
        rules=rules,
        requirements=requirements,
        visual=visual
    )


# Example usage and testing
if __name__ == "__main__":
    # Example: Create a connector graph
    graph = ConnectorGraph()

    # Add USD Composer template
    composer_connectors = [
        Connector("usd_input", ConnectorType.DATA_SOURCE, ConnectorProtocol.OMNIVERSE,
                 ConnectorDirection.INPUT, required=True),
        Connector("usd_output", ConnectorType.DATA_SINK, ConnectorProtocol.OMNIVERSE,
                 ConnectorDirection.OUTPUT),
        Connector("live_sync", ConnectorType.COMMUNICATION, ConnectorProtocol.WEBSOCKET,
                 ConnectorDirection.BIDIRECTIONAL)
    ]
    graph.add_template("usd_composer", composer_connectors)

    # Add USD Viewer template
    viewer_connectors = [
        Connector("usd_input", ConnectorType.DATA_SOURCE, ConnectorProtocol.OMNIVERSE,
                 ConnectorDirection.INPUT, required=True),
        Connector("live_sync", ConnectorType.COMMUNICATION, ConnectorProtocol.WEBSOCKET,
                 ConnectorDirection.BIDIRECTIONAL)
    ]
    graph.add_template("usd_viewer", viewer_connectors)

    # Check if they can connect
    can_connect, error = graph.can_connect("usd_composer", "usd_viewer",
                                          "usd_output", "usd_input")
    print(f"Can connect Composer to Viewer: {can_connect}")

    # Validate configuration
    valid, errors = graph.validate_configuration(["usd_viewer"])
    print(f"Configuration valid: {valid}")
    if errors:
        print("Errors:", errors)