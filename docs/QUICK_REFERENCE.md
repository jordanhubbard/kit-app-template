# Quick Reference Guide

Fast reference for common commands and workflows.

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd kit-app-template

# First time setup
./repo.sh  # Downloads SDK and dependencies

# Start visual development
cd kit_playground && ./dev.sh
# Then open: http://localhost:3000
```

---

## CLI Commands

### Template Management

```bash
# List all templates
./repo.sh template list

# Create application
./repo.sh template new \
  --template kit_base_editor \
  --name my_app

# Create with all options
./repo.sh template new \
  --template kit_base_editor \
  --name my_app \
  --display-name "My Application" \
  --version 1.0.0 \
  --per-app-deps \
  --standalone \
  --output-dir /path/to/output
```

### Building

```bash
# Build current application
cd source/apps/my_app
./repo.sh build --config release

# Build all applications
./repo.sh build --all --config release

# Clean build
./repo.sh build --config release --clean

# Parallel build (8 jobs)
./repo.sh build --config release -j8
```

### Launching

```bash
# Launch application
cd source/apps/my_app
./repo.sh launch --config release

# Launch with verbose logging
./repo.sh launch --config release --verbose

# Launch in portable mode
./repo.sh launch --config release --portable
```

### Application Management

```bash
# List all applications
./repo.sh list

# Register application
./repo.sh register --path source/apps/my_app

# Unregister application
./repo.sh unregister --name my_app
```

### Packaging

```bash
# Package for distribution
cd source/apps/my_app
./repo.sh package --config release
# Output in: _packages/
```

---

## UI Workflows

### Start Kit Playground

```bash
cd kit_playground
./dev.sh  # Linux/Mac
dev.bat   # Windows

# Opens http://localhost:3000
```

### Create Project (UI)

1. Click **"Templates"** → **"Applications"**
2. Click a **template card**
3. Click **"Create Project"**
4. Edit fields (or use defaults)
5. Click **"Create Project"** button
6. **Editor opens** with generated `.kit` file

### Build Project (UI)

1. In **Editor panel**, click **"Build"** button
2. **Build Output panel** shows progress
3. Wait for **"BUILD (RELEASE) SUCCEEDED"**
4. **"Launch" button** appears

### Launch Project (UI)

1. After successful build, click **"Launch"** button
2. **Launch Output** shows application startup
3. **Application window** opens

---

## File Locations

```bash
# Applications
source/apps/<app_name>/
├── <app_name>.kit          # Main config
├── config/                 # Settings
├── data/                   # Assets
└── docs/                   # Documentation

# Extensions
source/extensions/<ext.name>/
├── config/extension.toml   # Extension metadata
└── <ext>/<name>/          # Python package

# Build outputs
_build/<platform>/release/
├── kit/                    # Kit SDK
├── exts/                   # Extensions
└── <app_name>/            # Application

# Packages
_packages/
└── <app_name>-<version>-<platform>.zip
```

---

## Configuration Snippets

### Add Extension (.kit file)

```toml
[dependencies]
"omni.kit.window.viewport" = {}
"omni.kit.property.window" = {}
```

### Change Window Settings

```toml
[settings.app.window]
title = "My App"
width = 1920
height = 1080
```

### Enable Feature

```toml
[settings.exts."omni.kit.window.console"]
enabled = true
```

### Pin Extension Version

```toml
[dependencies]
"omni.kit.viewport.window" = { version = "2.3.1" }
```

---

## Common Issues

### Build Fails

```bash
# Clear cache and rebuild
rm -rf _build
./repo.sh tools clean
./repo.sh build --config release
```

### Launch Fails

```bash
# Try debug mode
./repo.sh launch --config debug --verbose
```

### Kit Playground Won't Start

```bash
cd kit_playground
./dev.sh  # Stop with Ctrl+C first

# Clear caches
rm -rf ui/node_modules/.vite
./dev.sh
```

### WebSocket Issues

```bash
# Kill zombie processes
pkill -f "python.*web_server"
pkill -f "npm.*dev"

# Restart
cd kit_playground && ./dev.sh
```

---

## Environment Variables

```bash
# Python unbuffered output
export PYTHONUNBUFFERED=1

# Custom backend port
export PLAYGROUND_BACKEND_PORT=5001

# Custom frontend port
export PLAYGROUND_FRONTEND_PORT=3001
```

---

## Useful Paths

| Path | Description |
|------|-------------|
| `source/apps/` | Application projects |
| `source/extensions/` | Extension projects |
| `templates/` | Available templates |
| `_build/` | Build artifacts |
| `_packages/` | Distribution packages |
| `_repo/` | Kit SDK and tools |
| `kit_playground/` | Visual development environment |
| `docs/` | Documentation |
| `ai-docs/` | Technical implementation docs |

---

## Port Reference

| Port | Service | URL |
|------|---------|-----|
| 3000 | Frontend UI | http://localhost:3000 |
| 5000 | Backend API | http://localhost:5000 |
| 5000 | API Docs | http://localhost:5000/api/docs |

---

## Template Types

| Template | Type | Use Case |
|----------|------|----------|
| `kit_base_editor` | Application | Full 3D editor |
| `omni_usd_viewer` | Application | USD file viewer |
| `omni_usd_composer` | Application | USD authoring tool |
| `base_application` | Application | Minimal starter |
| `kit_service` | Microservice | Headless service |
| `basic_python_extension` | Extension | Python extension |
| `basic_cpp_extension` | Extension | C++ extension |

---

## Git Workflows

### Create Feature Branch

```bash
git checkout -b feature/my-feature
# Make changes
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

### Update from Main

```bash
git checkout main
git pull
git checkout feature/my-feature
git merge main
```

---

## Debugging

### Enable Verbose Logging

```bash
./repo.sh launch --config debug --verbose
```

### Check Backend Logs

```bash
tail -f /tmp/kit-playground-backend.log
```

### Check Frontend Logs

```bash
tail -f /tmp/kit-playground-frontend.log
```

### Application Logs

```bash
# Linux
~/.nvidia-omniverse/logs/<app_name>/

# Windows
%USERPROFILE%\.nvidia-omniverse\logs\<app_name>\
```

---

## Performance Tips

### Faster Builds

```bash
# Use parallel jobs
./repo.sh build --config release -j$(nproc)

# Build only changed files
./repo.sh build --config release --incremental
```

### Reduce Dependencies

In `.kit` file, remove unused extensions from `[dependencies]`

### Use Release Builds

```bash
# Release is optimized
./repo.sh build --config release

# Debug has symbols but slower
./repo.sh build --config debug
```

---

## Extensions Reference

### Common Extensions

```toml
# UI and Windows
"omni.kit.uiapp" = {}                    # UI application base
"omni.kit.window.console" = {}           # Console window
"omni.kit.window.property" = {}          # Property editor
"omni.kit.window.viewport" = {}          # 3D viewport

# USD Support
"omni.usd" = {}                          # USD core
"omni.kit.usd.layers" = {}               # Layer management
"omni.kit.material.library" = {}         # Material browser

# Rendering
"omni.kit.renderer.core" = {}            # Renderer core
"omni.kit.renderer.capture" = {}         # Screenshot/video

# Services
"omni.services.transport.server.http" = {}   # HTTP server
"omni.kit.livestream.core" = {}              # Streaming
```

---

## Testing

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_template_creation.py

# With coverage
pytest --cov=kit_playground --cov-report=html

# Verbose
pytest -v
```

---

## Documentation

- **[User Guide](./USER_GUIDE.md)** - Complete workflows with examples
- **[Kit Playground Guide](./KIT_PLAYGROUND_GUIDE.md)** - Visual development
- **[API Documentation](./API_USAGE.md)** - API reference
- **[Architecture](./ARCHITECTURE.md)** - System design
- **[Template System](./TEMPLATE_SYSTEM.md)** - Template details

---

## Support

- **Kit SDK Docs**: https://docs.omniverse.nvidia.com/kit/
- **OpenUSD Docs**: https://openusd.org/
- **Omniverse Forums**: https://forums.developer.nvidia.com/c/omniverse/

---

**Last Updated:** 2024-10-27
