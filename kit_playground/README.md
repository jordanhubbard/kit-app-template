# Kit Playground

A web-based visual development environment for the NVIDIA Omniverse Kit SDK, inspired by Swift Playgrounds.

## Overview

Kit Playground provides an intuitive web interface for:
- Browsing and selecting templates from a visual gallery
- Customizing templates with an integrated code editor (Monaco)
- Building and running Kit projects directly from your browser
- Managing templates and dependencies automatically
- Quick prototyping and experimentation with Kit SDK

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
- Browser-based UI works on any platform
- Python backend inherits terminal environment for proper app launching
- No platform-specific builds required
- Lightweight and fast deployment

## Architecture

Kit Playground uses a simple web-based architecture:

1. **Frontend (kit_playground/ui/)**
   - React-based web UI with TypeScript
   - Material-UI components
   - Monaco code editor
   - Real-time updates via Socket.IO

2. **Backend (kit_playground/backend/)**
   - Flask REST API with Flask-SocketIO
   - Template management and discovery
   - Build system integration
   - Process management for launching Kit apps
   - Serves static React build files

3. **Core (kit_playground/core/)**
   - Template engine integration
   - Connector system implementation
   - Project lifecycle management

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for building the UI)
- Git
- NVIDIA RTX GPU (recommended for Kit apps)

### Option 1: Using Make (Linux/macOS)

```bash
# From the repository root
make playground
```

This will:
1. Check dependencies
2. Build the React UI
3. Start the Flask server
4. Open your browser to http://localhost:8081

### Option 2: Using the Launcher Scripts

**Linux/macOS:**
```bash
cd kit_playground
./playground.sh
```

**Windows:**
```batch
cd kit_playground
playground.bat
```

### Option 3: Manual Steps

```bash
# Build the UI
cd kit_playground/ui
npm install
npm run build

# Start the server
cd ../backend
python3 web_server.py --port 8200 --open-browser
```

### Development Mode (with hot reload)

**Terminal 1 - Backend:**
```bash
cd kit_playground/backend
python3 web_server.py --port 8200
```

**Terminal 2 - Frontend:**
```bash
cd kit_playground/ui
npm start
```

Then open http://localhost:3000 for React hot reload

## Usage

### Using Kit Playground

1. **Launch Kit Playground**
   ```bash
   make playground  # or ./playground.sh
   ```
   Your browser will open to http://localhost:8081

2. **Browse Templates**
   - View all available Kit templates in the gallery
   - Filter by type (Application, Extension, Component, Microservice)
   - See template descriptions and metadata

3. **Work with Templates**
   - Select a template to view details
   - Edit template code in the Monaco editor
   - Build templates using the build button
   - Run applications directly (they inherit your terminal environment)

4. **View Output**
   - See build logs in the integrated console
   - Applications launch in separate windows
   - Real-time updates via WebSocket connection

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
├── playground.sh          # Linux/macOS launcher
├── playground.bat         # Windows launcher
│
├── ui/                    # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── gallery/TemplateGallery.tsx
│   │   │   ├── editor/CodeEditor.tsx
│   │   │   ├── console/Console.tsx
│   │   │   ├── preview/PreviewPane.tsx
│   │   │   ├── connections/ConnectionEditor.tsx
│   │   │   ├── browser/TemplateBrowser.tsx
│   │   │   └── layout/MainLayout.tsx
│   │   ├── store/         # Redux store
│   │   └── services/      # API client
│   ├── package.json
│   └── build/            # Production build (generated)
│
├── backend/              # Flask Backend
│   └── web_server.py    # Main server with REST API
│
├── core/                 # Core Logic
│   └── playground_app.py # Application manager
│
└── tests/               # Test Suite
    └── test_backend.sh
```

## Configuration

Kit Playground can be configured via command-line arguments:

```bash
# Custom port
python3 backend/web_server.py --port 8201

# Custom host
python3 backend/web_server.py --host 0.0.0.0

# Auto-open browser
python3 backend/web_server.py --open-browser
```

The UI theme is dark by default (NVIDIA Green accent color).

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## License

This project is part of the NVIDIA Omniverse Kit SDK and is subject to the NVIDIA Software License Agreement.

## Current Status

**Implemented:**
- ✅ Template discovery and loading (13 templates)
- ✅ REST API backend with Flask
- ✅ React-based web UI
- ✅ Monaco code editor integration
- ✅ Template gallery with metadata
- ✅ Build system integration
- ✅ Process management for launching apps
- ✅ WebSocket real-time updates
- ✅ Cross-platform launcher scripts

**In Progress:**
- 🔄 Enhanced code editing features
- 🔄 Visual connection editor
- 🔄 Project persistence
- 🔄 Template customization

**Planned:**
- 📋 AI-assisted template generation
- 📋 Cloud deployment options
- 📋 Template marketplace integration
- 📋 Collaborative editing