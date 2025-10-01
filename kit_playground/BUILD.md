# Kit Playground - Build Instructions

## Overview

Kit Playground is an Electron application with two build modes:

1. **Container builds (Recommended)**: Build in Docker container - no Node.js required on host
2. **Native builds**: Build directly on host - requires Node.js/npm installation

Both modes support Linux x86_64 and ARM64 (electron-builder auto-detects architecture).

## System Requirements

### Container Builds (Recommended)
**Host requirements:**
- Docker
- Python 3.8+
- Git

**No Node.js needed on host!** All Node.js dependencies are in the container.

### Native Builds
**Host requirements:**
- Node.js 16+ and npm 7+
- Python 3.8+
- Git
- Standard build tools: `build-essential` (for native npm modules)
- FUSE 2 (for running AppImage)
- GTK dependencies: `libgtk-3-0` and `libnotify4`

### Windows Native Builds
- Node.js 16+ and npm 7+
- Python 3.8+
- Git
- Visual Studio Build Tools (for native npm modules)

---

## Quick Start (Development Mode)

### 1. Install Dependencies

```bash
cd kit_playground

# Install Node.js dependencies
npm install

# Install Python backend dependencies
pip install -r backend/requirements.txt
```

### 2. Run in Development

```bash
# Option 1: Using npm
npm run dev

# Option 2: Using repo script
cd ..
./repo.sh playground

# Option 3: Using Makefile
cd ..
make playground
```

This will:
1. Start React dev server on http://localhost:3000
2. Launch Electron app
3. Spawn Python backend on http://localhost:8081
4. Enable hot-reload for development

---

## Building Production Distributable

### Method 1: Container Build (Recommended - No Node.js on Host)

**From repo root:**
```bash
# Build in container and launch
make playground

# Or just build without launching
make playground-build
```

This creates: `kit_playground/ui/dist/Kit Playground-1.0.0.AppImage` (for your architecture)

**Benefits:**
- ✅ No Node.js installation needed on host
- ✅ Consistent build environment
- ✅ Works on both x86_64 and ARM64
- ✅ Isolated dependencies

### Method 2: Native Build (Requires Node.js)

**Linux:**
```bash
cd kit_playground

# Option 1: Use build script
./build.sh

# Option 2: Use Makefile (from repo root)
cd ..
make playground-build-native

# Option 3: Manual steps
cd kit_playground/ui
npm install --legacy-peer-deps
npm run build
npm run dist
```

**Windows:**
```cmd
cd kit_playground
build.bat
```

**Benefits:**
- ✅ Faster builds (no Docker overhead)
- ✅ Direct access to system resources

---

## Build Output Structure

After building, you'll find:

```
kit_playground/
├── ui/
│   ├── build/          # Compiled React app (npm run build)
│   │   └── index.html
│   ├── dist/           # Electron distributables (npm run dist)
│   │   ├── Kit Playground-1.0.0.AppImage           # Linux (x86_64 or ARM64)
│   │   └── Kit Playground Setup 1.0.0.exe          # Windows
│   └── node_modules/   # Dependencies
```

---

## Dependency Installation Details

### How Dependencies Are Installed

#### Frontend (Electron + React)
```bash
npm install
```

This installs from `package.json`:
- **Electron**: `electron@^27.0.0`
- **Electron Builder**: `electron-builder@^24.0.0`
- **React**: `react@^18.2.0`, `react-dom@^18.2.0`
- **Material-UI**: `@mui/material@^5.13.0`
- **Monaco Editor**: `@monaco-editor/react@^4.6.0`
- **Redux**: `@reduxjs/toolkit@^1.9.5`, `react-redux@^8.0.5`
- And many more...

All dependencies are downloaded from **public npm registry**.

#### Backend (Python Flask)
```bash
pip install -r backend/requirements.txt
```

This installs:
- `flask>=3.0.0`
- `flask-cors>=4.0.0`
- `flask-socketio>=5.3.0`
- `python-socketio>=5.10.0`
- `eventlet>=0.33.0`

All from **public PyPI**.

### Bundled Resources

When building with `electron-builder`, these are bundled into the app:

1. **Templates** (`../templates/`) - All Kit SDK templates
2. **Tools** (`../tools/`) - Template engine, repoman, packman
3. **Backend** (`backend/`) - Python Flask server
4. **Node modules** - Only production dependencies

---

## Testing the Build

### Test Development Build

```bash
cd kit_playground
npm start
```

Should open the Electron app with all features working.

### Test Production Build

**Linux:**
```bash
cd kit_playground/ui/dist

# Make executable
chmod +x "Kit Playground-1.0.0.AppImage"

# Run
./"Kit Playground-1.0.0.AppImage"
```

**Windows:**
```cmd
cd kit_playground\ui\dist
"Kit Playground Setup 1.0.0.exe"
```

---

## Build System Architecture

### electron-builder Configuration

In `package.json`, the `"build"` section configures:

```json
{
  "appId": "com.nvidia.kit-playground",
  "productName": "Kit Playground",
  "files": [
    "electron/**/*",      // Electron main/preload
    "build/**/*",         // React build output
    "backend/**/*",       // Python backend
    "node_modules/**/*"   // Dependencies
  ],
  "extraResources": [
    { "from": "../tools", "to": "tools" },
    { "from": "../templates", "to": "templates" }
  ],
  "linux": {
    "target": "AppImage",
    "category": "Development"
  }
}
```

### What Gets Bundled

1. **Electron Runtime** - Chromium + Node.js (~150MB)
2. **React App** - Compiled JavaScript (~5MB)
3. **Python Backend** - Source files (~2MB)
4. **Templates + Tools** - Kit SDK tools (~50MB)
5. **Node Modules** - Production deps (~100MB)

**Total AppImage size**: ~300-400MB

---

## Platform Support

### ✅ Supported Platforms

- **Linux x86_64**: Full support (Ubuntu 22.04+, other distros)
- **Linux ARM64**: Full support (Raspberry Pi, AWS Graviton, etc.)
- **Windows x86_64**: Full support (Windows 10+)

### Quick Build Commands

**Linux:**
```bash
# From repo root
make playground-build

# Or from kit_playground directory
./build.sh

# Output: ui/dist/Kit Playground-1.0.0.AppImage
```

**Windows:**
```cmd
# From kit_playground directory
build.bat

REM Output: ui\dist\Kit Playground Setup 1.0.0.exe
```

---

## Troubleshooting

### Issue: "electron-builder: command not found"

**Solution**: Install dependencies first
```bash
cd kit_playground
npm install
```

### Issue: "Python backend fails to start"

**Solution**: Install Python dependencies
```bash
pip install -r backend/requirements.txt
```

### Issue: AppImage won't run

**Solution**: Install FUSE
```bash
sudo apt-get install fuse libfuse2
```

### Issue: Build fails with "Missing GTK"

**Solution**: Install GTK dependencies
```bash
sudo apt-get install libgtk-3-0 libnotify4 libnss3 libxss1
```

---

## CI/CD Considerations

For automated builds:

```yaml
# .github/workflows/build.yml
name: Build Kit Playground

on: [push]

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd kit_playground
          npm install
          pip install -r backend/requirements.txt

      - name: Build AppImage
        run: |
          cd kit_playground
          npm run build
          npm run dist

      - name: Upload AppImage
        uses: actions/upload-artifact@v3
        with:
          name: kit-playground-linux
          path: kit_playground/dist/*.AppImage
```

---

## Summary

**Recommended: Container Builds**
- **Requires on host:** Docker, Python, Git (NO Node.js needed!)
- **Command:** `make playground` or `make playground-build`
- **Works on:** Linux x86_64, Linux ARM64
- **Output:** `ui/dist/Kit Playground-1.0.0.AppImage` (~350MB)

**Alternative: Native Builds**
- **Requires on host:** Node.js, npm, Python, Git
- **Command:** `./build.sh` (Linux) or `build.bat` (Windows)
- **Works on:** Linux x86_64, Linux ARM64, Windows x86_64
- **Output:** AppImage (Linux) or `.exe` (Windows)

**Key Points:**
- ✅ Container builds = no Node.js on host
- ✅ Both modes support x86_64 and ARM64
- ❌ No cross-platform builds (Linux→Windows)
- ✅ All dependencies from public registries (npm, PyPI)