# Kit App Template - Project Memory

## Project Overview

**Name:** kit-app-template
**Version:** 108.0 (Kit SDK 108.0.0)
**Repository Size:** ~15MB (source only, excluding build artifacts)
**Organization:** NVIDIA-Omniverse
**Purpose:** A comprehensive toolkit for developing GPU-accelerated applications using the NVIDIA Omniverse Kit SDK

### Description

The kit-app-template is a sophisticated development framework that provides:
- **Streamlined Development**: Pre-configured templates and tools for creating OpenUSD-based applications
- **Cross-Platform Support**: Native support for Windows and Linux development
- **GPU Acceleration**: Full utilization of NVIDIA GPU capabilities for visualization and simulation
- **Extensibility**: Modular architecture supporting Python and C++ extensions
- **Visual Development**: Kit Playground - a visual development environment inspired by Swift Playgrounds
- **Cloud-Ready**: Built-in support for streaming applications to web browsers and cloud deployment

### Key Use Cases

1. Creating immersive 3D applications and editors
2. Building USD content authoring and viewing tools
3. Developing headless microservices for automation
4. Generating synthetic data for AI training
5. Streaming GPU-accelerated applications to browsers

---

## Repository Structure

### Core Directories

```
kit-app-template/
├── _build/                    # Build output directory (gitignored)
│   ├── linux-x86_64/         # Linux build artifacts
│   ├── windows-x86_64/       # Windows build artifacts
│   └── deps/                  # Dependency configuration
├── _compiler/                 # Compiler-generated files (gitignored)
├── _repo/                     # Repository tools and dependencies (gitignored)
├── .github/                   # GitHub workflows and templates
├── .vscode/                   # VS Code configuration
│   ├── launch.json           # Debug configurations
│   ├── settings.json         # Editor settings
│   └── tasks.json            # Build tasks
├── docs/                      # Additional documentation
├── kit_playground/            # Visual development environment
│   ├── backend/              # Python backend API
│   ├── core/                 # Core playground logic
│   ├── electron/             # Electron app wrapper
│   ├── ui/                   # React-based frontend
│   ├── BUILD.md              # Build documentation
│   ├── Dockerfile            # Container definition
│   └── playground.py         # Main entry point
├── readme-assets/             # Documentation assets and guides
├── source/                    # Generated application source code
│   ├── apps/                 # Generated .kit application files
│   └── extensions/           # Generated extension code
├── templates/                 # Template system
│   ├── applications/         # Application templates
│   ├── components/           # Reusable components
│   ├── config/               # Configuration templates
│   ├── extensions/           # Extension templates
│   ├── microservices/        # Microservice templates
│   └── template_registry.toml # Template metadata and relationships
├── tools/                     # Development tools
│   ├── deps/                 # Dependency definitions
│   ├── packman/              # Package manager
│   └── repoman/              # Repository management tools
│       ├── connector_system.py
│       ├── launch.py
│       ├── package.py
│       ├── repo_dispatcher.py
│       ├── template_engine.py
│       ├── template_helper.py
│       └── template_validator.py
├── CHANGELOG.md              # Version history
├── CLAUDE.md                 # AI assistant instructions
├── LICENSE                   # NVIDIA Software License Agreement
├── Makefile                  # Cross-platform build automation
├── premake5.lua              # Build configuration
├── README.md                 # Main documentation
├── repo.bat                  # Windows entry point
├── repo.sh                   # Linux/Mac entry point
├── repo.toml                 # Main configuration
├── repo_tools.toml           # Tool definitions
├── SECURITY.md               # Security policies
├── TEMPLATE_SYSTEM.md        # Template system documentation
└── user-config-example.toml  # Example user configuration
```

### Important Files

- **repo.sh / repo.bat**: Main CLI entry points for all operations (template creation, building, launching)
- **repo.toml**: Central configuration (build settings, registry URLs, packaging rules)
- **Makefile**: High-level build orchestration with dependency checking
- **premake5.lua**: Lower-level build configuration
- **templates/template_registry.toml**: Template discovery and relationship definitions

---

## Build System & Tooling

### Build Architecture

The project uses a multi-layered build system designed for cross-platform compatibility:

1. **Top Layer: Makefile** (User-facing)
   - OS detection (Linux, macOS, Windows)
   - Dependency checking (Python, Node.js, Docker, Git)
   - High-level commands (`make build`, `make playground`, `make test`)
   - Platform-specific installation helpers

2. **Middle Layer: repo.sh/repo.bat** (Command Dispatcher)
   - OS-neutral Python-based command dispatcher
   - Template operations
   - Build orchestration
   - Application launching
   - Package creation

3. **Bottom Layer: premake5.lua** (Build Configuration)
   - Kit SDK integration via `repo_kit_tools`
   - C++17 configuration
   - Application generation from .kit files
   - Dependency copying

### Key Tools

#### repoman (tools/repoman/)

Python-based repository management system providing:

- **template_engine.py**: Data-driven template generation with variable interpolation
- **template_validator.py**: Validates configurations and generated files
- **launch.py**: Application launcher with guided selection
- **package.py**: Guided packaging tool for distribution
- **connector_system.py**: Visual programming connection system for Kit Playground
- **repo_dispatcher.py**: OS-independent command routing

#### packman (tools/packman/)

NVIDIA's package manager for pulling Kit SDK and dependencies:
- Version: 7.29 (updated to address network restriction issues)
- Handles large file downloads
- Caches dependencies

### Build Commands

```bash
# Core workflow
make build              # Build all applications
make playground         # Launch Kit Playground (container-based)
make test              # Run test suite
make clean             # Clean build artifacts

# Alternative commands via repo.sh
./repo.sh build        # Build applications
./repo.sh launch       # Launch application (interactive)
./repo.sh test         # Run tests
./repo.sh package      # Package for distribution

# Template operations
./repo.sh template list                    # List available templates
./repo.sh template docs <template_name>    # View template documentation
./repo.sh template new <template_name> \
  --name=company.app \
  --display-name="My App" \
  --version=1.0.0                         # Create from template
```

### Container-Based Development

The project supports Docker-based builds (especially for Kit Playground):

```bash
make playground           # Build in container and launch (no Node.js needed on host)
make playground-dev       # Native development mode (requires Node.js)
make playground-shell     # Interactive container shell for debugging
make playground-clean     # Remove all build artifacts and images
```

---

## Template System

### Architecture

The template system is **data-driven** and **hierarchical**, supporting:
- Self-documentation
- Configuration inheritance
- Variable interpolation
- Automatic validation
- Standalone project generation

### Template Types

1. **Applications** (`templates/applications/`)
   - **kit_base_editor**: Minimal OpenUSD editor
   - **omni_usd_composer**: Scene authoring and composition
   - **omni_usd_explorer**: Large scene exploration
   - **omni_usd_viewer**: Viewport-only streaming-optimized viewer

2. **Extensions** (`templates/extensions/`)
   - **Python**:
     - `basic_python_extension`: Minimal Python extension
     - `basic_python_ui_extension`: Python UI extension
   - **C++**:
     - `basic_cpp_extension`: Minimal C++ extension
     - `basic_python_binding`: C++ with Python bindings via Pybind11

3. **Microservices** (`templates/microservices/`)
   - **kit_service**: Headless REST API service

4. **Components** (`templates/components/`)
   - Setup extensions (composer, explorer, viewer)
   - Streaming layers (default, NVCF, GDN)

### Template Registry (template_registry.toml)

Defines:
- **Discovery paths**: Where to find template.toml files
- **Type definitions**: Categories and their icons
- **Relationships**: Dependencies and suggestions between templates
- **Compatibility**: Platform and version requirements

Example relationships:
```toml
"omni_usd_viewer.requires" = ["omni_usd_viewer_setup", "omni_usd_viewer_messaging"]
"basic_python_extension.suggests" = ["basic_python_ui_extension"]
```

### Template Configuration System

Templates support configuration inheritance and variable interpolation:

```toml
# User configuration (~/.omni/kit-app-template/user.toml)
[company]
name = "my_company"
display_name = "My Company"

[project]
author = "${user.name}"
copyright = "Copyright (c) 2024 ${company.display_name}"

# Project configuration
[application]
name = "${company.name}.${project.name}"  # Interpolated: my_company.my_app
```

### Standalone Project Generation

Templates can be generated as self-contained projects:

```bash
./repo.sh template new kit_service \
  --name my_company.my_api \
  --display-name "My API Service" \
  --output-dir ./my-standalone-project
```

Generated projects include:
- Complete source code
- Build tooling (repo.sh, premake5.lua)
- All necessary configuration
- Independent git repository

---

## Kit Playground

### Overview

Kit Playground is a **visual development environment** for Kit applications, inspired by Swift Playgrounds. It provides a side-by-side editor and live preview experience.

**Technology Stack:**
- **Frontend**: React 18 + TypeScript + Material-UI
- **Editor**: Monaco Editor (VS Code engine)
- **Backend**: Python Flask/FastAPI
- **Desktop App**: Electron 38
- **Visual Programming**: React Flow Renderer

### Architecture

```
Kit Playground Architecture:

Frontend (React + Electron)
├── Template Gallery (Material-UI)
├── Code Editor (Monaco)
├── Connection Editor (React Flow)
└── Console/Output Viewer

Backend (Python)
├── Template Management API
├── Build System Integration
├── Process Manager
└── WebSocket Server (live updates)

Core
├── Connector System
├── Template Discovery
├── Dependency Resolution
└── Project Management
```

### Features

1. **Visual Template Gallery**: Browse, search, and filter templates with thumbnails
2. **Side-by-Side Development**: Code on left, live preview on right
3. **Device Preview Modes**: Desktop, Tablet, Phone, 4K/TV with zoom controls
4. **Visual Connection System**: Drag-and-drop template connections with validation
5. **Integrated Build & Run**: One-click build, run, and console output
6. **Deployment Options**: Export standalone or deploy to cloud

### Build System

Kit Playground supports two build modes:

1. **Container-Based** (default, no Node.js required on host):
   ```bash
   make playground              # Build in Docker and launch
   make playground-build        # Build distributable
   make playground-shell        # Debug in container
   ```

2. **Native** (requires Node.js 16+ on host):
   ```bash
   make playground-dev          # Development mode with hot reload
   make playground-build-native # Native build
   ```

### Connector System

The connector system (tools/repoman/connector_system.py) enables visual template composition:

```python
# Connectors define input/output interfaces
{
  "provides": [
    {"name": "usd_output", "type": "file", "format": "usd"}
  ],
  "requires": [
    {"name": "scene_file", "type": "file", "format": "usd"}
  ]
}
```

Connections are validated for compatibility and can be uni-directional or bi-directional.

### Package.json Key Scripts

```json
{
  "start": "concurrently react + electron",
  "dev": "Development mode with hot reload",
  "build": "Production build",
  "dist": "electron-builder for AppImage/exe/dmg"
}
```

---

## Development Workflows

### Creating a New Application

**CLI Method:**
```bash
# 1. List available templates
./repo.sh template list --type application

# 2. View template documentation
./repo.sh template docs kit_base_editor

# 3. Create application
./repo.sh template new kit_base_editor \
  --name my_company.my_editor \
  --display-name "My Editor" \
  --version 1.0.0

# 4. Build
./repo.sh build

# 5. Launch
./repo.sh launch
```

**Visual Method (Kit Playground):**
```bash
# 1. Launch playground
make playground

# 2. Browse gallery and select template
# 3. Customize in editor
# 4. Click Build → Run
# 5. Export or deploy
```

### Adding Extensions

```bash
# Create Python extension
./repo.sh template new basic_python_extension \
  --name my_company.my_extension \
  --display-name "My Extension"

# Create C++ extension
./repo.sh template new basic_cpp_extension \
  --name my_company.my_cpp_ext
```

**Note**: C++ development on Windows requires:
- Visual Studio 2019/2022 with "Desktop development with C++" workload
- Windows SDK
- Set `repo.toml`: `link_host_toolchain = true` and `build.enabled = true` for Windows platform

### Testing

```bash
# Run all tests
./repo.sh test

# Run specific test suite
./repo.sh test templates

# Validate specific template
python3 tools/repoman/template_validator.py test --template=kit_base_editor

# Validate all templates
python3 tools/repoman/template_validator.py test-all
```

### Packaging & Distribution

```bash
# Interactive packaging
./repo.sh package

# Two package types generated:
# - Fat package: Includes Kit SDK (~larger)
# - Thin package: Excludes Kit SDK (requires registry access)
```

Packages follow NVIDIA Omniverse naming convention:
```
archive_name@{build_version}+{gitbranch}.{builder_id}.{githash}.{build_environment}.{host_platform}.{archive_format}
```

### Application Streaming

The project supports three streaming configurations:

1. **Self-Managed**: Omniverse Kit App Streaming (Kubernetes)
2. **NVIDIA Cloud Functions (NVCF)**: Managed GPU cloud
3. **Graphics Delivery Network (GDN)**: Global CDN streaming

Add streaming during template creation:
```bash
./repo.sh template new kit_base_editor --name my_app
# Choose "Yes" for application layers
# Select streaming configuration
```

---

## Key Technologies

### Core Stack

- **Language Support**: Python 3.8+, C++17
- **Build System**: premake5, GNU Make, MSBuild (Windows)
- **Package Management**: packman (NVIDIA), pip, npm
- **USD Foundation**: OpenUSD for 3D content
- **GPU Acceleration**: NVIDIA RTX, CUDA-enabled

### Kit SDK

- **Version**: 108.0.0 (Feature Branch)
- **Purpose**: Omniverse application framework
- **Capabilities**:
  - OpenUSD scene manipulation
  - GPU-accelerated rendering (RTX)
  - Extension system (Python/C++)
  - Streaming infrastructure
  - Cloud deployment ready

### Kit Playground Stack

- **Frontend**: React 18.2, TypeScript 5, Material-UI 5
- **Desktop**: Electron 38
- **Editor**: Monaco Editor 0.44
- **State**: Redux Toolkit
- **Build**: electron-builder, react-scripts
- **Backend**: Python 3, Flask/FastAPI (implied)
- **Communication**: WebSocket (socket.io)

### Extension Registry

The project pulls extensions from:
```toml
[registry]
kit/default = "https://ovextensionsprod.blob.core.windows.net/exts/kit/prod/${kit_version_major}/shared"
kit/sdk = "https://ovextensionsprod.blob.core.windows.net/exts/kit/prod/sdk/${kit_version_short}/${kit_git_hash}"
kit/community = "https://dw290v42wisod.cloudfront.net/exts/kit/community"
```

---

## Important Context & Conventions

### Development Philosophy (from CLAUDE.md)

1. **Container-first**: Always use Docker if available, avoid running commands directly on host that operate on source code
2. **Makefile as API**: Check Makefile first before trying shell commands
3. **Cross-platform**: Write complex functionality in OS-neutral Python, provide both .sh and .bat scripts
4. **Auto-commit**: Auto git commit and push after major changes without asking permission
5. **Public packages**: Assume running outside NVIDIA network, use public package sources
6. **Template compliance**: New templates must follow template checker dictates

### Naming Conventions

- **Applications**: `company.product` (lowercase, dot-separated)
- **Extensions**: `company.extension_name` (lowercase, underscores)
- **Display Names**: "Product Name" (title case)
- **Versions**: Semantic versioning (major.minor.patch)

### Platform Support

**Officially Supported:**
- Linux: Ubuntu 22.04+ (primary development platform)
- Windows: Windows 10/11 with VS 2019/2022

**Minimum Requirements:**
- NVIDIA RTX GPU (RTX 3070+ recommended)
- NVIDIA Driver: 537.58+
- Git + Git LFS
- Internet access (for SDK and extension downloads)

### File Permissions & Execution

The project is designed to work across platforms:
- All repo.sh/build.sh scripts are executable (755)
- Cross-platform Python dispatcher handles OS differences
- Makefile handles platform detection automatically

### Configuration Hierarchy

Configuration precedence (lowest to highest):
1. Template defaults (templates/*/template.toml)
2. Base configuration (templates/config/base.toml)
3. Company configuration (templates/config/company.toml)
4. User configuration (~/.omni/kit-app-template/user.toml)
5. Project configuration (project-config.toml)
6. Command-line arguments

---

## Recent Changes & History

### Current State (as of Oct 1, 2025)

**Branch**: main (clean working directory)
**Latest Version**: 108.0
**Last Commit**: `88a5bcc` - Fix: Update critical dependencies to address security vulnerabilities

### Recent Development Focus (Last 10 Commits)

1. **Security**: Updated dependencies to address vulnerabilities
2. **Kit Playground**: Major refactor to container-based builds
   - Restored container-based builds (no Node.js requirement on host)
   - Added comprehensive Makefile
   - Implemented cross-platform Electron builder
   - Added Docker-based build system
   - Complete implementation with all missing components
3. **Cleanup**: Removed unused test scripts

### Major Version Changes (from CHANGELOG)

**108.0.0 (2025-08-19)**
- Kit SDK 108.0.0 update
- Renamed "Omniverse Cloud Streaming" → "NVCF Streaming"
- Updated streaming extensions (omni.kit.livestream.app)
- Aligned to default ports (removed custom overrides)
- Enabled USD Viewer messaging extension testing
- Fixed duplicate key issues in .kit files

**107.3.0 (2025-05-27)**
- Added `repo template modify` for adding layers to existing apps
- Updated packman to 7.29 (network restriction fixes)

**107.0.3 (2025-03-20)**
- Individual application layer selection
- C++ with Python Extension template added
- Developer Bundle extensions by default
- Streaming configuration documentation

**106.5.0 (2024-12-12)**
- Asset browser URL updates
- OVC streaming optimizations

### Known Issues & Considerations

1. **Windows C++ Development**: Requires manual Visual Studio configuration and `link_host_toolchain = true`
2. **First Launch**: Initial shader compilation takes 5-8 minutes
3. **Path Restrictions**: Tooling checks for whitespace in paths and OneDrive paths
4. **Docker Required**: For container-based Kit Playground builds
5. **Feature Branch**: This repo uses Kit SDK Feature Branch (regularly updated, best for testing/prototyping)
6. **Production Use**: For stable production, use Production Branch from NGC

### Template System Evolution

- **Legacy**: Interactive prompts (deprecated)
- **Current**: Data-driven with command-line arguments or config files
- **Enhanced**: Hierarchical organization, self-documentation, composition
- **Future**: AI-assisted development, template marketplace (roadmap)

---

## Security & Licensing

### Security Policy

**Do not report security issues via GitHub.**

Report vulnerabilities to:
- Web: https://www.nvidia.com/object/submit-security-vulnerability.html
- Email: psirt@nvidia.com (PGP key available)

### License

**NVIDIA Software License Agreement** with **Product-Specific Terms for Omniverse**

Key files:
- LICENSE
- PRODUCT_TERMS_OMNIVERSE

### Data Collection

Anonymous usage data is collected for:
- Performance improvement
- Diagnostic purposes

**No personal information** (email, name) is collected.
Data collection can be configured in application settings.

---

## Quick Reference Commands

### Essential Commands

```bash
# Setup
make deps                    # Check dependencies
make install-deps           # Install missing dependencies

# Development
make build                  # Build applications
./repo.sh launch           # Launch application
./repo.sh test             # Run tests

# Templates
./repo.sh template list                           # List all
./repo.sh template list --type application        # Filter by type
./repo.sh template docs <name>                    # View docs
./repo.sh template new <template> --name=my.app   # Create

# Kit Playground
make playground            # Build in container and launch
make playground-dev        # Native dev mode with hot reload
make playground-clean      # Clean all artifacts

# Package
./repo.sh package          # Create distribution packages
```

### File Locations

**Configuration:**
- Main: `repo.toml`
- Templates: `templates/template_registry.toml`
- User config: `~/.omni/kit-app-template/user.toml`

**Generated Code:**
- Applications: `source/apps/*.kit`
- Extensions: `source/extensions/`

**Build Output:**
- Linux: `_build/linux-x86_64/`
- Windows: `_build/windows-x86_64/`

**Documentation:**
- Main: `README.md`
- Template system: `TEMPLATE_SYSTEM.md`
- Kit Playground: `kit_playground/README.md` + `BUILD.md`
- Additional: `readme-assets/additional-docs/`

---

## Development Tips

### For AI Assistants

1. **Always check CLAUDE.md** for project-specific instructions
2. **Use containers when available**: Prefer Docker-based workflows
3. **Check Makefile first**: It defines the high-level API
4. **Auto-commit allowed**: Git commit and push after major changes
5. **Cross-platform**: Provide both .sh and .bat for new scripts
6. **Template validation**: Always validate after template generation

### For Developers

1. **Start with templates**: Don't build from scratch
2. **Use Kit Playground**: For visual, beginner-friendly workflow
3. **Check documentation**: Each template has self-documentation
4. **Test early**: Run `./repo.sh test` frequently
5. **Validate templates**: Use template_validator.py
6. **Read the tutorial**: https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/

### Common Workflows

**Quick prototype:**
```bash
make playground
# Browse → Select → Customize → Build → Run
```

**Production application:**
```bash
./repo.sh template new kit_base_editor --name my.app
./repo.sh build
./repo.sh test
./repo.sh package
```

**Extension development:**
```bash
./repo.sh template new basic_python_extension --name my.ext
# Edit source/extensions/my.ext/
./repo.sh build
./repo.sh launch  # Select app that uses your extension
```

---

## Additional Resources

### Documentation

- Kit SDK Manual: https://docs.omniverse.nvidia.com/kit/docs/kit-manual/
- Kit App Template Tutorial: https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/
- DLI Course: https://learn.nvidia.com/courses/course-v1:DLI+S-OV-11+V1
- Release Notes: https://docs.omniverse.nvidia.com/dev-guide/latest/release-notes/

### In-Repo Guides

- Usage and Troubleshooting: `readme-assets/additional-docs/usage_and_troubleshooting.md`
- Windows Developer Config: `readme-assets/additional-docs/windows_developer_configuration.md`
- Kit App Streaming: `readme-assets/additional-docs/kit_app_streaming_config.md`
- Developer Bundle Extensions: `readme-assets/additional-docs/developer_bundle_extensions.md`
- Tooling Guide: `readme-assets/additional-docs/kit_app_template_tooling_guide.md`

### Community

- GitHub: https://github.com/NVIDIA-Omniverse/kit-app-template
- Issues: https://github.com/NVIDIA-Omniverse/kit-app-template/issues
- NGC (Production): https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/collections/omniverse_enterprise_25h1

---

## Kit Playground - Current State (Oct 1, 2025)

### Implementation Status

**Frontend (React + Electron):** ✅ FULLY IMPLEMENTED
- Complete UI with TemplateGallery, CodeEditor, PreviewPane
- Redux state management
- Split-pane layout with tabs
- Material-UI components
- Monaco editor integration

**Backend (Python + Flask):** ✅ FULLY WORKING
- Web server responds to health checks ✓
- REST API endpoints defined ✓
- Template discovery FIXED - now returns all 13 templates ✓
- Returns complete metadata: name, display_name, description, category, type

**Root Cause (FIXED):**
Missing `tomli` and `tomli-w` Python packages. The TemplateEngine uses these to parse
template.toml files. Without them, template discovery silently failed.

**Dependencies:**
- Python backend requires: flask, flask-cors, flask-socketio, python-socketio, eventlet, tomli, tomli-w
- Installation: `pip install -r kit_playground/backend/requirements.txt`
- **IMPORTANT**: Updated requirements.txt to include tomli and tomli-w

**Testing Backend:**
```bash
cd kit_playground
bash test_backend.sh
```

Expected flow once fixed:
1. User opens AppImage → Electron launches
2. Electron spawns `python3 backend/web_server.py --port 8081`
3. React UI loads, calls `/api/templates`
4. Backend returns template list from `templates/template_registry.toml`
5. User selects template → UI shows details
6. User clicks "Build" → Backend runs `./repo.sh build`
7. User clicks "Run" → Backend runs `./repo.sh launch`

---

**Last Updated:** October 1, 2025
**Kit SDK Version:** 108.0.0
**Project State:** Kit Playground backend partially functional, template discovery needs fix
