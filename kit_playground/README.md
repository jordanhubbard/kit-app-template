# Kit Playground

A cross-platform visual development environment for the NVIDIA Omniverse Kit SDK, inspired by Swift Playgrounds.

## Overview

Kit Playground provides an intuitive, visual interface for:
- Browsing and selecting templates from a visual gallery
- Customizing templates with an integrated code editor
- Connecting templates via drag-and-drop visual programming
- Building and running projects without leaving the playground
- Managing data sources and dependencies automatically

## Features

### Visual Template Gallery
- Thumbnail previews for all templates
- Filter by type, category, and capabilities
- See connector compatibility at a glance
- Search and tag-based discovery

### Smart Connector System
- Visual connection management
- Automatic compatibility checking
- Bi-directional and uni-directional connectors
- Real-time validation of connections
- Data source resolution with user prompts

### Integrated Development
- Syntax-highlighted code editor
- Live preview and hot reload
- Integrated debugging tools
- Code snippets and templates
- IntelliSense/autocomplete support

### Cross-Platform Support
- Native applications for Windows, Linux, and macOS
- Consistent experience across platforms
- Platform-specific optimizations
- Cloud-ready deployment options

## Architecture

Kit Playground is built as a modular application with:

1. **Frontend (kit_playground/frontend/)**
   - Cross-platform UI using Qt6 or Electron
   - Visual template gallery
   - Node-based connection editor
   - Integrated code editor (Monaco/CodeMirror)

2. **Backend (kit_playground/backend/)**
   - Template management API
   - Build system integration
   - Process management for running apps
   - WebSocket server for live updates

3. **Core (kit_playground/core/)**
   - Connector system implementation
   - Template discovery and loading
   - Dependency resolution
   - Configuration management

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for web-based frontend)
- Git and Git LFS
- NVIDIA RTX GPU (for full functionality)

### Installation

```bash
# Clone the repository
git clone https://github.com/NVIDIA-Omniverse/kit-app-template.git
cd kit-app-template/kit_playground

# Install dependencies
pip install -r requirements.txt
npm install  # If using web frontend

# Run the playground
python playground.py
```

### Development Setup

```bash
# Set up development environment
./setup.sh  # Linux/macOS
.\setup.bat # Windows

# Run in development mode
python playground.py --dev
```

## Usage

### Creating a New Project

1. **Launch Kit Playground**
   ```bash
   python playground.py
   ```

2. **Browse Templates**
   - Scroll through the visual gallery
   - Click on a template to see details
   - View connector specifications

3. **Customize Template**
   - Click "Customize" to open the editor
   - Modify template parameters
   - Add custom code

4. **Connect Templates**
   - Drag from output connector to input connector
   - System validates compatibility
   - Resolve any missing data sources

5. **Build and Run**
   - Click "Build" to compile
   - Click "Run" to launch
   - View output in integrated console

### Template Connection Example

```python
# Connect USD Composer to USD Viewer
composer = playground.add_template("omni_usd_composer")
viewer = playground.add_template("omni_usd_viewer")

# Create connection
playground.connect(
    from_template=composer,
    from_connector="usd_output",
    to_template=viewer,
    to_connector="usd_input"
)

# Resolve requirements
composer.set_requirement("scene_file", "/path/to/scene.usd")

# Build and run
playground.build_all()
playground.run_all()
```

## Project Structure

```
kit_playground/
├── README.md
├── requirements.txt
├── setup.py
├── playground.py           # Main entry point
│
├── frontend/               # UI Layer
│   ├── web/               # Web-based UI (Electron/Browser)
│   │   ├── index.html
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── components/
│   │   │   │   ├── TemplateGallery.tsx
│   │   │   │   ├── ConnectionEditor.tsx
│   │   │   │   ├── CodeEditor.tsx
│   │   │   │   └── Console.tsx
│   │   │   └── services/
│   │   └── package.json
│   │
│   └── native/            # Native UI (Qt/PyQt)
│       ├── main_window.py
│       ├── widgets/
│       └── resources/
│
├── backend/               # Backend Services
│   ├── api.py            # REST API
│   ├── websocket.py      # WebSocket server
│   ├── build_service.py  # Build system
│   ├── process_manager.py # Process management
│   └── storage.py        # Project persistence
│
├── core/                  # Core Logic
│   ├── template_loader.py
│   ├── connector_engine.py
│   ├── dependency_resolver.py
│   ├── project_manager.py
│   └── config.py
│
├── assets/               # Static Assets
│   ├── icons/
│   ├── themes/
│   └── templates/
│
└── tests/               # Test Suite
    ├── test_connectors.py
    ├── test_templates.py
    └── test_integration.py
```

## Configuration

Kit Playground can be configured via `playground.config.toml`:

```toml
[playground]
theme = "dark"
auto_save = true
hot_reload = true

[editor]
font_size = 14
tab_size = 4
syntax_theme = "monokai"

[build]
parallel_builds = true
cache_enabled = true
output_directory = "_build"

[server]
port = 8080
host = "localhost"
enable_ssl = false
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## License

This project is part of the NVIDIA Omniverse Kit SDK and is subject to the NVIDIA Software License Agreement.

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Template specification with connectors
- ✅ Connector system implementation
- 🔄 Basic UI framework
- 🔄 Template gallery

### Phase 2: Core Features
- Template customization editor
- Visual connection editor
- Build system integration
- Process management

### Phase 3: Advanced Features
- Cloud deployment
- Collaboration features
- AI-assisted development
- Template marketplace

### Phase 4: Ecosystem
- Plugin system
- Community templates
- Enterprise features
- Mobile companion app