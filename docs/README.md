# Kit App Template - Getting Started Guide

**Version**: 2.0 (All 6 Phases Complete)
**Last Updated**: October 24, 2025

## Overview

Kit App Template is a powerful, GPU-accelerated application development framework for NVIDIA Omniverse. This guide covers the enhanced CLI with full automation support, per-app dependency isolation, and standalone project generation.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Common Workflows](#common-workflows)
5. [CLI Reference](#cli-reference)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 30-Second Start

```bash
# 1. Clone the repository
git clone https://github.com/jordanhubbard/kit-app-template.git
cd kit-app-template

# 2. List available templates
./repo.sh template list

# 3. Create your first application
./repo.sh template new kit_base_editor \
  --name my.first.app \
  --accept-license

# 4. Build and launch
./repo.sh build
./repo.sh launch my.first.app
```

### What You Get

- **Templates**: Pre-configured application, extension, and microservice templates
- **CLI**: Powerful command-line interface with JSON output for automation
- **Build System**: Integrated build and launch system
- **Dependency Management**: Isolated or shared Kit SDK dependencies
- **Standalone Projects**: Self-contained, portable applications
- **REST API**: Complete API for programmatic access

---

## Installation

### Prerequisites

- **Linux**: Ubuntu 20.04+ or CentOS 7+
- **Windows**: Windows 10+ with WSL2 or native
- **Python**: 3.7+ (bundled with packman)
- **Git**: For cloning and version control
- **Disk Space**: ~10GB for Kit SDK and dependencies

### Setup

```bash
# Clone repository
git clone https://github.com/jordanhubbard/kit-app-template.git
cd kit-app-template

# The repo.sh script will automatically:
# - Download dependencies (packman)
# - Pull Kit SDK (on first build)
# - Set up build environment
```

### Verify Installation

```bash
# Check CLI is working
./repo.sh --help

# List available templates
./repo.sh template list

# Check Python and dependencies
./repo.sh tools check
```

---

## Core Concepts

### 1. Templates

Templates are pre-configured starting points for applications, extensions, and microservices.

**Available Templates**:
- `kit_base_editor` - Full-featured Omniverse editor application
- `omni_usd_viewer` - USD file viewer application
- `omni_usd_explorer` - USD exploration application
- `omni_usd_composer` - USD composition application
- `basic_python_extension` - Python extension template
- `basic_cpp_extension` - C++ extension template
- `kit_service` - Microservice template

**View All Templates**:
```bash
./repo.sh template list
./repo.sh template list --type application
./repo.sh template list --json | jq .
```

### 2. Projects

Projects are created from templates and can be:
- **Standard Projects**: Located in `source/apps/` or `source/extensions/`
- **Standalone Projects**: Self-contained with own build system
- **Per-App Dependency Projects**: Isolated Kit SDK per application

### 3. Build System

The build system uses:
- **Premake5**: For generating build files
- **Packman**: For dependency management
- **Kit SDK**: NVIDIA Omniverse Kit runtime

### 4. Dependency Models

**Global Dependencies** (default):
- Shared Kit SDK in `_build/` directory
- All apps use same Kit version
- Faster downloads, uses less disk space

**Per-App Dependencies** (new):
- Isolated Kit SDK per app in `source/apps/<name>/_kit/`
- Each app can use different Kit version
- Prevents conflicts, enables custom configurations

**See**: [Per-App Dependencies Guide](../PER_APP_DEPENDENCIES.md)

---

## Common Workflows

### Create and Launch an Application

```bash
# 1. Create from template
./repo.sh template new kit_base_editor \
  --name com.company.myapp \
  --display-name "My Application" \
  --version "1.0.0" \
  --accept-license

# 2. Build
./repo.sh build

# 3. Launch
./repo.sh launch com.company.myapp

# 4. Launch in headless mode (for streaming/CI)
./repo.sh launch com.company.myapp --no-window
```

### Create a Standalone Application

Standalone applications include their own build system and can be distributed independently.

```bash
# Create standalone project
./repo.sh template new kit_base_editor \
  --name my.app \
  --standalone \
  --output-dir /path/to/standalone/my.app

# Build in standalone directory
cd /path/to/standalone/my.app
./repo.sh build

# Launch
./repo.sh launch my.app
```

**See**: [Standalone Projects Guide](../STANDALONE_PROJECTS.md)

### Create Application with Isolated Dependencies

```bash
# Create with per-app dependencies
./repo.sh template new kit_base_editor \
  --name my.isolated.app \
  --per-app-deps

# The app will have its own Kit SDK in:
# source/apps/my.isolated.app/_kit/

# Build and launch (auto-detects per-app Kit)
./repo.sh build --app my.isolated.app
./repo.sh launch my.isolated.app
```

### Automation and CI/CD

```bash
# JSON output for scripting
./repo.sh template list --json | jq '.templates[] | .name'

# Create project with JSON output
./repo.sh template new kit_base_editor \
  --name ci.test.app \
  --json \
  --accept-license > output.json

# Extract playback file from JSON
playback=$(jq -r '.playback_file' output.json)

# Quiet mode for minimal output
./repo.sh template new kit_base_editor \
  --name quiet.app \
  --quiet \
  --accept-license
```

### Extension Development

```bash
# Create Python extension
./repo.sh template new basic_python_extension \
  --name com.company.my_extension

# Create C++ extension
./repo.sh template new basic_cpp_extension \
  --name com.company.my_cpp_extension

# Build and test
./repo.sh build
./repo.sh launch kit_base_editor  # Extensions auto-load
```

### Microservice Development

```bash
# Create microservice
./repo.sh template new kit_service \
  --name my.service

# Build
./repo.sh build --app my.service

# Launch
./repo.sh launch my.service
```

---

## CLI Reference

### Template Commands

#### `template list`

List all available templates.

```bash
./repo.sh template list [options]

Options:
  --type <type>     Filter by type (application, extension, microservice)
  --json            Output as JSON
  --verbose         Verbose output
  --quiet           Minimal output
```

**Examples**:
```bash
# List all templates
./repo.sh template list

# List only applications
./repo.sh template list --type application

# JSON output for scripting
./repo.sh template list --json
```

#### `template docs`

Show documentation for a specific template.

```bash
./repo.sh template docs <template-name>
```

**Examples**:
```bash
# View template documentation
./repo.sh template docs kit_base_editor
./repo.sh template docs basic_python_extension
```

#### `template new`

Create a new project from a template.

```bash
./repo.sh template new <template-name> [options]

Required:
  <template-name>   Name of template (use 'template list' to see options)

Options:
  --name <name>             Project name (e.g., com.company.app)
  --display-name <name>     Human-readable name (default: project name)
  --version <version>       Version number (default: 1.0.0)

Automation:
  --accept-license          Accept license without prompt
  --batch-mode              Non-interactive mode with defaults
  --json                    JSON output for scripting
  --verbose                 Verbose output with details
  --quiet                   Minimal output

Advanced:
  --standalone              Create self-contained project
  --output-dir <path>       Output directory (for standalone)
  --per-app-deps            Use isolated Kit SDK for this app
  --add-layers <layer>      Add additional layers (comma-separated)
```

**Examples**:
```bash
# Basic application
./repo.sh template new kit_base_editor \
  --name my.app \
  --accept-license

# With all options
./repo.sh template new kit_base_editor \
  --name com.company.myapp \
  --display-name "My Application" \
  --version "1.0.0" \
  --accept-license \
  --verbose

# Standalone application
./repo.sh template new kit_base_editor \
  --name my.standalone \
  --standalone \
  --output-dir ~/projects/my.standalone

# With per-app dependencies
./repo.sh template new kit_base_editor \
  --name my.isolated.app \
  --per-app-deps

# JSON output for automation
./repo.sh template new kit_base_editor \
  --name auto.app \
  --json \
  --accept-license | jq .
```

### Build Commands

#### `build`

Build projects in the repository.

```bash
./repo.sh build [options]

Options:
  --config <config>    Build configuration (release, debug)
  --app <name>         Build specific app only
  --target <target>    Build specific target
  --clean              Clean before building
```

**Examples**:
```bash
# Build all projects
./repo.sh build

# Build specific app
./repo.sh build --app my.app

# Debug build
./repo.sh build --config debug

# Clean build
./repo.sh build --clean
```

### Launch Commands

#### `launch`

Launch a built application.

```bash
./repo.sh launch <app-name> [options]

Required:
  <app-name>    Application name (with or without .kit extension)

Options:
  --config <config>    Launch configuration (release, debug)
  --no-window          Headless mode (for streaming/CI)
  --xpra               Launch with Xpra (remote display)
  -- <args>            Additional Kit arguments (after --)
```

**Examples**:
```bash
# Launch application
./repo.sh launch my.app

# Launch in headless mode
./repo.sh launch my.app --no-window

# Launch with Kit arguments
./repo.sh launch my.app -- --verbose --ext-folder /path/to/exts

# Launch with Xpra (remote display)
./repo.sh launch my.app --xpra
```

---

## Advanced Features

### Per-App Dependencies

Isolate Kit SDK and dependencies per application to prevent conflicts.

**When to Use**:
- Different apps need different Kit versions
- Testing with experimental Kit builds
- Custom Kit configurations per app
- Avoiding dependency conflicts

**Usage**:
```bash
# Create app with per-app deps
./repo.sh template new kit_base_editor \
  --name my.isolated.app \
  --per-app-deps

# Configure Kit version (edit source/apps/my.isolated.app/dependencies/kit-deps.toml)
[kit_sdk]
version = "106.0"

[cache]
strategy = "isolated"

# Build and launch (auto-detects isolated Kit)
./repo.sh build --app my.isolated.app
./repo.sh launch my.isolated.app
```

**See**: [PER_APP_DEPENDENCIES.md](../PER_APP_DEPENDENCIES.md)

### Kit App Streaming

Enable WebRTC streaming for remote browser access to Kit applications.

**When to Use**:
- Remote development and collaboration
- Cloud-based GPU rendering
- Browser-based application demos
- Headless deployment environments
- Zero-install user experience

**Create Streaming App** (CLI):
```bash
# Create app with streaming enabled
./repo.sh template new kit_base_editor \
  --name my.streaming.app \
  --accept-license

# Manually enable streaming (or use API/UI)
# Edit source/apps/my.streaming.app/my.streaming.app.kit
# Add to [dependencies] section:
[dependencies]
"omni.services.streaming.webrtc" = {}
"omni.kit.streamhelper" = {}
```

**Launch Streaming App**:
```bash
# Build the app
./repo.sh build --app my.streaming.app

# Launch with streaming (auto-detected or forced)
./repo.sh launch my.streaming.app.kit --streaming

# Custom port
./repo.sh launch my.streaming.app.kit --streaming --streaming-port 48000
```

**Expected Output**:
```
========================================
Kit App Streaming (WebRTC) Mode
========================================
Port: 47995
URL:  https://localhost:47995
========================================

Starting streaming server...
Waiting for streaming server on port 47995...

========================================
✓ Streaming Ready!
========================================
URL: https://localhost:47995
========================================

Note: Self-signed SSL certificate warning is normal.
Accept the certificate in your browser to continue.
```

**Browser Access**:
1. Open: `https://localhost:47995`
2. Accept SSL certificate warning (self-signed)
3. Your Kit application streams live in the browser! 🎉

**API/UI Creation**:
```bash
# Via REST API
curl -X POST http://localhost:5000/api/templates/create \
  -H "Content-Type: application/json" \
  -d '{
    "template": "kit_base_editor",
    "name": "my.streaming.app",
    "enableStreaming": true
  }'

# Via Web UI
# 1. Navigate to http://localhost:3000/templates
# 2. Select template
# 3. Check "Enable Kit App Streaming" in Advanced Options
# 4. Create project
```

**Technical Details**:
- **Protocol**: WebRTC over HTTPS
- **Default Port**: 47995 (configurable)
- **Latency**: ~50-100ms (local), ~100-300ms (remote)
- **Extensions Required**:
  - `omni.services.streaming.webrtc` - WebRTC streaming server
  - `omni.kit.streamhelper` - Streaming helper utilities
- **SSL**: Self-signed certificate by default (override with `--/rtx/webrtc/certificatePath` and `--/rtx/webrtc/privateKeyPath`)

**See**: [KIT_APP_STREAMING_DESIGN.md](../KIT_APP_STREAMING_DESIGN.md), [API_USAGE.md](API_USAGE.md#kit-app-streaming-launch)

### Standalone Projects

Create self-contained projects that can be distributed without the main repository.

**When to Use**:
- Distributing applications to other developers
- Creating portable demos
- Independent project development
- Custom deployment scenarios

**Usage**:
```bash
# Create standalone
./repo.sh template new kit_base_editor \
  --name my.standalone \
  --standalone \
  --output-dir ~/projects/my.standalone

# Work in standalone directory
cd ~/projects/my.standalone
./repo.sh build
./repo.sh launch my.standalone
```

**See**: [STANDALONE_PROJECTS.md](../STANDALONE_PROJECTS.md)

### JSON Mode for Automation

Use `--json` flag for machine-readable output in CI/CD pipelines.

```bash
# Get template list as JSON
./repo.sh template list --json | jq '.templates[] | .name'

# Create project and capture output
result=$(./repo.sh template new kit_base_editor \
  --name auto.app \
  --json \
  --accept-license)

# Extract fields from JSON
status=$(echo "$result" | jq -r '.status')
playback=$(echo "$result" | jq -r '.playback_file')
path=$(echo "$result" | jq -r '.path')

# Use in scripts
if [ "$status" = "success" ]; then
  echo "Project created at: $path"
  ./repo.sh build --app auto.app
fi
```

### REST API Access

The Kit Playground provides a REST API for programmatic access.

```bash
# Start API server
cd kit_playground/backend
python3 web_server.py

# API available at http://localhost:5000
# Swagger UI at http://localhost:5000/api/docs

# Use with curl (see docs/API_USAGE.md)
curl http://localhost:5000/api/templates/list
```

**See**: [API_USAGE.md](API_USAGE.md)

---

## Troubleshooting

### Common Issues

#### License Not Accepted

**Error**: `License terms have not been accepted`

**Solution**:
```bash
./repo.sh template new <template> --name <name> --accept-license
```

#### Build Failures

**Error**: `Build failed` or dependency errors

**Solutions**:
```bash
# Clean build
./repo.sh build --clean

# Update dependencies
rm -rf _build/_repo/deps
./repo.sh build

# Check Python dependencies
./repo.sh tools check
```

#### Launch Issues

**Error**: `Application failed to launch`

**Solutions**:
```bash
# Check build succeeded
./repo.sh build --app <name>

# Launch with verbose output
./repo.sh launch <name> -- --verbose

# Check logs
cat _build/logs/<name>.log

# For headless/CI environments
./repo.sh launch <name> --no-window
```

#### Extension Not Loading

**Error**: Extension not found or not loading

**Solutions**:
```bash
# Verify extension built
ls _build/<platform>/<config>/exts/<extension-name>

# Check extension is enabled in app
./repo.sh launch <app> -- --ext-folder <path> --enable <extension>

# Build in debug mode for more info
./repo.sh build --config debug
```

### Getting Help

```bash
# CLI help
./repo.sh --help
./repo.sh template --help
./repo.sh build --help

# Template documentation
./repo.sh template docs <template-name>

# Check project status
./repo.sh tools check

# View build logs
less _build/logs/build.log
```

### Additional Resources

- **Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **API Usage**: [docs/API_USAGE.md](API_USAGE.md)
- **Per-App Dependencies**: [PER_APP_DEPENDENCIES.md](../PER_APP_DEPENDENCIES.md)
- **Standalone Projects**: [STANDALONE_PROJECTS.md](../STANDALONE_PROJECTS.md)
- **Migration Guide**: [MIGRATION_TO_PER_APP_DEPS.md](../MIGRATION_TO_PER_APP_DEPS.md)

---

## Next Steps

1. **Create Your First App**: `./repo.sh template new kit_base_editor --name my.app`
2. **Build and Launch**: `./repo.sh build && ./repo.sh launch my.app`
3. **Explore Templates**: `./repo.sh template list`
4. **Read Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
5. **Try Standalone Mode**: [STANDALONE_PROJECTS.md](../STANDALONE_PROJECTS.md)
6. **Set Up Automation**: Use `--json` flags and REST API

---

**Happy Building with Kit App Template!** 🚀
