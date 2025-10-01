# Cross-Platform Electron Build Guide

This document describes the cross-platform build system for Kit Playground, which enables building Windows Electron applications from Linux containers or detecting Windows for bare-metal builds.

## Overview

The Kit Playground now supports multiple build strategies:

1. **Docker-based builds** - Using `electronuserland/builder:wine` for cross-platform builds
2. **Native builds** - Building directly on the host OS
3. **Hybrid approach** - Automatic detection and fallback strategies

## Build Methods

### Method 1: Docker-based Cross-Platform Builds (Recommended)

This method uses Docker with Wine to build Windows applications from Linux:

```bash
# Build for Windows using Docker
make playground-build-windows

# Build for all platforms using Docker
make playground-build-all

# Or use the Python script directly
cd kit_playground
python3 cross_platform_builder.py --target windows --docker
```

**Advantages:**
- ✅ Works on any Linux system with Docker
- ✅ Consistent build environment
- ✅ No need to install Wine directly
- ✅ Supports Windows, Linux, and macOS targets

**Requirements:**
- Docker installed and running
- Internet connection (to pull Docker images)

### Method 2: Native Cross-Platform Builds

This method builds directly on the host system:

```bash
# Build for current platform natively
make playground-build-native

# Build for Windows natively (requires Wine on Linux)
make playground-build-native-windows

# Or use the Python script directly
cd kit_playground
python3 cross_platform_builder.py --target windows
```

**Advantages:**
- ✅ Faster builds (no Docker overhead)
- ✅ Direct access to system resources
- ✅ Works without Docker

**Requirements:**
- Node.js 16+ and npm
- Python 3.8+
- Wine (for Windows builds on Linux)

### Method 3: Automatic Detection

The cross-platform builder automatically detects the best build strategy:

```bash
cd kit_playground
python3 cross_platform_builder.py
```

The script will:
1. Detect the current OS and available tools
2. Choose the optimal build strategy
3. Fall back to alternative methods if needed

## Build Targets

### Windows Builds

**From Linux with Docker:**
```bash
make playground-build-windows
# or
python3 cross_platform_builder.py --target windows --docker
```

**From Linux with Wine:**
```bash
# Install Wine first
sudo apt-get install wine
# Then build
python3 cross_platform_builder.py --target windows
```

**From Windows:**
```bash
# Native Windows build
python cross_platform_builder.py --target windows
```

### Linux Builds

**From Linux:**
```bash
python3 cross_platform_builder.py --target linux
```

**From other platforms with Docker:**
```bash
python3 cross_platform_builder.py --target linux --docker
```

### macOS Builds

**From macOS:**
```bash
python3 cross_platform_builder.py --target macos
```

**Note:** macOS builds require macOS due to code signing limitations.

## Output Files

Built applications are placed in `kit_playground/ui/dist/`:

- **Windows:** `Kit Playground Setup 1.0.0.exe`
- **Linux:** `Kit Playground-1.0.0.AppImage`
- **macOS:** `Kit Playground-1.0.0.dmg`

## Environment Detection

The build system automatically detects:

- Operating system (Windows, Linux, macOS)
- Available tools (Docker, Wine, Node.js, Python)
- Docker images (electronuserland/builder:wine)

Example detection output:
```
🖥️  System: Linux
🐳 Docker: ✅
🍷 Wine: ✅
📦 Node.js: ✅
🐍 Python: ✅

🎯 Build strategy: docker
📝 Reason: Using Docker with Wine for Windows build on Linux
```

## Configuration

### Package.json Scripts

New npm scripts have been added to `ui/package.json`:

```json
{
  "scripts": {
    "dist:windows": "npm run build && electron-builder --win --publish=never",
    "dist:linux": "npm run build && electron-builder --linux --publish=never",
    "dist:macos": "npm run build && electron-builder --mac --publish=never",
    "build:cross-platform": "python3 ../cross_platform_builder.py",
    "build:windows": "python3 ../cross_platform_builder.py --target windows",
    "build:linux": "python3 ../cross_platform_builder.py --target linux",
    "build:docker": "python3 ../cross_platform_builder.py --docker"
  }
}
```

### Makefile Targets

New make targets have been added:

```makefile
make playground-build-windows      # Build for Windows using Docker
make playground-build-all          # Build for all platforms using Docker
make playground-build-native       # Build natively (current platform)
make playground-build-native-windows # Build for Windows natively
```

### Docker Configuration

The `Dockerfile` has been enhanced to support cross-platform builds:

- Based on `electronuserland/builder:wine`
- Includes Python 3 for the build script
- Pre-installs dependencies
- Supports caching for faster builds

## Troubleshooting

### Docker Issues

**Problem:** Docker image not found
```bash
docker pull electronuserland/builder:wine
```

**Problem:** Permission denied
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Wine Issues

**Problem:** Wine not installed on Linux
```bash
sudo apt-get update
sudo apt-get install wine
```

**Problem:** Wine configuration needed
```bash
winecfg  # Configure Wine if needed
```

### Node.js Issues

**Problem:** Node.js version too old
```bash
# Install Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Build Failures

**Problem:** Out of memory during build
```bash
# Increase Docker memory limit or use native build
python3 cross_platform_builder.py --target windows  # Native build
```

**Problem:** Missing dependencies
```bash
cd kit_playground/ui
npm install  # Reinstall dependencies
```

## OS-Agnostic Code Audit

The codebase has been audited to ensure OS-agnostic functionality:

### ✅ OS-Agnostic Components

1. **Python Tools** (`tools/repoman/`):
   - `repo_dispatcher.py` - Uses `os.name` and `Path` for cross-platform paths
   - `template_engine.py` - Platform-independent template processing
   - `template_helper.py` - Pure Python, no OS-specific code

2. **Build Scripts**:
   - `repo.sh` / `repo.bat` - Platform-specific wrappers for same functionality
   - `cross_platform_builder.py` - New unified build script

3. **Electron App**:
   - `main.js` - Uses `process.platform` for OS detection
   - Cross-platform file paths using `path.join()`
   - OS-specific menu handling

### ✅ Platform Detection Patterns

The codebase consistently uses these patterns:

```python
# Python
import os
import platform

if os.name == "nt":  # Windows
    # Windows-specific code
elif platform.system() == "Linux":
    # Linux-specific code
```

```javascript
// Node.js/Electron
if (process.platform === 'win32') {
    // Windows-specific code
} else if (process.platform === 'linux') {
    // Linux-specific code
}
```

### ✅ Path Handling

All path operations use cross-platform methods:

```python
# Python - using pathlib
from pathlib import Path
path = Path("tools") / "packman" / "python.sh"

# Python - using os.path
import os
path = os.path.join("tools", "packman", "python.sh")
```

```javascript
// Node.js
const path = require('path');
const scriptPath = path.join(__dirname, 'backend', 'web_server.py');
```

## Integration with Existing Build System

The cross-platform build system integrates seamlessly with the existing build infrastructure:

1. **Makefile Integration** - New targets added without breaking existing ones
2. **Docker Integration** - Enhanced existing Dockerfile
3. **npm Scripts** - Added new scripts alongside existing ones
4. **Repository Structure** - No changes to existing file organization

## Future Enhancements

Potential improvements for the cross-platform build system:

1. **CI/CD Integration** - GitHub Actions workflows for automated builds
2. **Code Signing** - Automated signing for Windows and macOS builds
3. **Build Caching** - Enhanced caching for faster subsequent builds
4. **ARM Support** - Support for ARM64 builds on Apple Silicon and Linux ARM
5. **Notarization** - macOS notarization support

## Summary

The cross-platform build system provides:

✅ **Windows builds from Linux containers** using Docker + Wine
✅ **Automatic platform detection** and build strategy selection
✅ **OS-agnostic Python helper script** for bare-metal Windows builds
✅ **Maintained OS-agnostic codebase** for applications and extensions
✅ **Seamless integration** with existing build infrastructure
✅ **Comprehensive documentation** and troubleshooting guides

The solution addresses both requirements:
1. Building Windows Electron apps in Linux containers
2. Ensuring OS-agnostic functionality throughout the codebase
