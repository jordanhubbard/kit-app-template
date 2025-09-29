# Enhanced Template Specification v2.0

## Overview

This document defines the enhanced template descriptor format that supports visual representation, connector specifications, and inter-template communication rules for the Kit Playground system.

## Enhanced Template Descriptor Format

```toml
# Enhanced template.toml format with visual and connector specifications

[metadata]
name = "template_name"
display_name = "Template Display Name"
type = "application|extension|microservice|component"
category = "editor|viewer|service|connector"
description = "Brief template description"
version = "1.0.0"
author = "Author Name"
license = "License Type"

# Visual representation - base64 encoded thumbnail (256x256 recommended)
[metadata.visual]
thumbnail = """
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
"""
icon = "material-icon-name"  # Alternative: Material Design icon name
color_scheme = "#FF5722"     # Primary color for UI representation

[metadata.compatibility]
platforms = ["linux-x86_64", "windows-x86_64", "darwin-x86_64"]
min_kit_version = "108.0.0"
languages = ["python", "c++"]

# Connector Specifications
[connectors]
# Define what this template can connect to and how

[[connectors.inputs]]
name = "usd_scene"
type = "data_source"
protocol = "omniverse"
direction = "input"  # Can only receive
required = true
description = "USD scene data input"
mime_types = ["model/vnd.usd", "model/vnd.usda", "model/vnd.usdc"]

[[connectors.inputs]]
name = "config"
type = "configuration"
protocol = "json"
direction = "input"
required = false
description = "Configuration data"
schema = "config_schema.json"

[[connectors.outputs]]
name = "rendered_frames"
type = "data_sink"
protocol = "streaming"
direction = "output"  # Can only send
required = false
description = "Rendered frame output stream"
mime_types = ["image/png", "image/jpeg", "video/mp4"]

[[connectors.bidirectional]]
name = "collaboration"
type = "communication"
protocol = "websocket"
direction = "bidirectional"
required = false
description = "Real-time collaboration channel"
compatible_with = ["omni_usd_composer", "omni_usd_explorer"]

# Connector Rules and Contracts
[connector_rules]
# Define interaction rules with other templates

[[connector_rules.allows]]
template = "omni_usd_composer"
connector = "collaboration"
mode = "bidirectional"
description = "Can collaborate with USD Composer"

[[connector_rules.requires]]
template = "kit_service"
connector = "usd_scene"
mode = "input"
description = "Requires USD scene service"

[[connector_rules.provides]]
template = "*"  # Wildcard - any template
connector = "rendered_frames"
mode = "output"
description = "Can provide rendered output to any consumer"

[[connector_rules.excludes]]
template = "competing_renderer"
reason = "Incompatible rendering pipeline"

# Data requirements that can prompt user interaction
[requirements]

[[requirements.data_sources]]
id = "primary_usd_source"
name = "Primary USD Scene"
type = "file_path"
mime_types = ["model/vnd.usd", "model/vnd.usda", "model/vnd.usdc"]
required = true
prompt = "Please select the primary USD scene file"
default_path = "${env.HOME}/Documents/Omniverse"
validation = "file_exists"

[[requirements.data_sources]]
id = "texture_directory"
name = "Texture Assets"
type = "directory_path"
required = false
prompt = "Select directory containing texture assets (optional)"
default_path = "${project.root}/assets/textures"

[[requirements.services]]
id = "nucleus_server"
name = "Nucleus Server"
type = "service_endpoint"
protocol = "omniverse"
required = true
prompt = "Enter Nucleus server URL"
default = "omniverse://localhost"
validation = "url_reachable"

[[requirements.credentials]]
id = "api_key"
name = "API Key"
type = "secure_string"
required = false
prompt = "Enter API key for external services (optional)"
validation = "regex:^[A-Za-z0-9]{32,}$"

# Template-specific configuration
[template]
class = "ApplicationTemplate"
source_dir = "../../apps/template_name"
extends = "base_application"  # Template inheritance

# UI hints for Kit Playground
[playground]
# Configuration for how this template appears in Kit Playground

[playground.editor]
syntax_highlighting = "python"
code_templates = ["basic_setup.py", "advanced_features.py"]
snippets_enabled = true
intellisense = true

[playground.preview]
default_viewport = "3d"  # 2d, 3d, split
enable_live_reload = true
debug_mode_available = true

[playground.actions]
# Custom actions available in the playground
[[playground.actions.custom]]
name = "Generate Physics"
command = "generate_physics"
icon = "physics"
shortcut = "Ctrl+Shift+P"

[[playground.actions.custom]]
name = "Optimize Scene"
command = "optimize_scene"
icon = "speed"
shortcut = "Ctrl+Shift+O"

# Variables for template instantiation
[variables]
application_name = "my_app"
application_display_name = "My Application"
version = "0.1.0"
enable_streaming = false
enable_collaboration = false

# Documentation embedded in template
[documentation]
overview = """
Comprehensive overview of what this template provides,
its purpose, and primary use cases.
"""

use_cases = [
    "Real-time visualization",
    "Collaborative editing",
    "Batch processing"
]

key_features = [
    "Feature 1 with description",
    "Feature 2 with description"
]

getting_started = """
Step-by-step guide for using this template
"""

examples = [
    {
        name = "Basic Example",
        description = "Simple usage example",
        code = """
# Example code snippet
from omni.kit import app
app.startup()
"""
    }
]

# Dependencies with enhanced specifications
[dependencies]
required_extensions = [
    "omni.kit.window.viewport",
    "omni.kit.renderer.core"
]

optional_extensions = [
    "omni.kit.collaboration",
    "omni.kit.streaming.native"
]

# Build configuration
[build]
requires_build = true
build_commands = [
    "./repo.sh build --config release",
    "./repo.sh package"
]

[deployment]
supports_packaging = true
supports_containerization = true
supports_cloud = true
cloud_providers = ["aws", "azure", "gcp", "nvcf"]
```

## Connector Types and Protocols

### Connector Types
- **data_source**: Provides data input (files, streams, databases)
- **data_sink**: Accepts data output
- **configuration**: Configuration data exchange
- **communication**: Inter-process or network communication
- **compute**: Computational resources or services
- **ui_component**: UI elements that can be embedded

### Connector Protocols
- **omniverse**: Omniverse-specific protocols (USD, MDL, etc.)
- **http/https**: REST APIs
- **websocket**: Real-time bidirectional communication
- **grpc**: High-performance RPC
- **file**: Local file system access
- **streaming**: Audio/video streaming protocols
- **json**: JSON data exchange
- **graphql**: GraphQL API

### Direction Modes
- **input**: Can only receive data
- **output**: Can only send data
- **bidirectional**: Can both send and receive

## Template Interaction Rules

### Rule Types
1. **allows**: Templates this can connect with
2. **requires**: Templates this must have available
3. **provides**: Services this template offers
4. **excludes**: Templates that are incompatible

### Validation Rules
- Circular dependencies are not allowed
- Required connectors must be satisfied
- Incompatible templates cannot be connected
- Data types must match between connectors

## Kit Playground Integration

The enhanced template format enables Kit Playground to:

1. **Visual Template Gallery**
   - Display thumbnails for each template
   - Show connector compatibility visually
   - Filter by type, category, and capabilities

2. **Interactive Configuration**
   - Prompt for missing data sources
   - Validate connections before building
   - Show real-time compatibility checks

3. **Smart Recommendations**
   - Suggest compatible templates
   - Auto-configure connections
   - Resolve dependency chains

4. **Live Development**
   - Edit template code in playground
   - Hot reload on changes
   - Debug with integrated tools

## Implementation Notes

### Embedding Images
Images should be base64 encoded and kept under 100KB for thumbnails. Format:
```
data:image/png;base64,[base64_encoded_data]
```

### Connector Validation
The system validates:
- Protocol compatibility
- Data type matching
- Required vs optional connections
- Circular dependency detection

### User Prompts
When requirements cannot be auto-resolved, Kit Playground will:
1. Display a user-friendly dialog
2. Provide browse buttons for file/directory selection
3. Validate input before proceeding
4. Store preferences for future use

## Migration Path

Existing templates will be migrated by:
1. Adding default thumbnail (auto-generated from template type)
2. Inferring basic connectors from dependencies
3. Setting sensible defaults for new fields
4. Maintaining backward compatibility

## Example: USD Composer Enhanced Template

```toml
[metadata]
name = "omni_usd_composer"
display_name = "USD Composer"
type = "application"
category = "editor"
description = "Full-featured USD scene authoring application"
version = "2.0.0"

[metadata.visual]
thumbnail = "data:image/png;base64,..."  # Actual thumbnail data
icon = "edit_3d"
color_scheme = "#4CAF50"

[connectors]
[[connectors.inputs]]
name = "usd_scene"
type = "data_source"
protocol = "omniverse"
direction = "input"
required = true

[[connectors.outputs]]
name = "usd_export"
type = "data_sink"
protocol = "omniverse"
direction = "output"

[[connectors.bidirectional]]
name = "live_sync"
type = "communication"
protocol = "websocket"
direction = "bidirectional"
compatible_with = ["omni_usd_explorer", "omni_usd_viewer"]

[connector_rules]
[[connector_rules.allows]]
template = "omni_usd_explorer"
connector = "live_sync"
mode = "bidirectional"

[requirements]
[[requirements.data_sources]]
id = "scene_file"
name = "USD Scene"
type = "file_path"
mime_types = ["model/vnd.usd"]
required = false
prompt = "Select USD scene to open (optional)"
```

This enhanced specification provides the foundation for building Kit Playground as a visual, interactive development environment for the Omniverse ecosystem.