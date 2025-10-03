# Kit Playground - Build Instructions

## Overview

Kit Playground is a web-based application with two build modes:

1. **Container builds (Recommended)**: Build in Docker container - no Node.js required on host
2. **Native builds**: Build directly on host - requires Node.js/npm installation

Both modes support Linux x86_64 and ARM64.

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
1. Build the React UI
2. Start Python Flask backend on http://localhost:8888
3. Open web browser to the application
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

This creates: `kit_playground/ui/build/` (production-optimized React build)

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
│   └── node_modules/   # Dependencies
├── backend/
│   └── web_server.py   # Flask backend server
```

---

## Dependency Installation Details

### How Dependencies Are Installed

#### Frontend (React)
```bash
npm install
```

This installs from `package.json`:
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

When building for production, these are packaged together:

1. **Templates** (`../templates/`) - All Kit SDK templates
2. **Tools** (`../tools/`) - Template engine, repoman, packman
3. **Backend** (`backend/`) - Python Flask server
4. **React Build** (`ui/build/`) - Compiled frontend assets

---

## Testing the Build

### Test Development Build

```bash
cd kit_playground
npm start
```

Should start the React dev server at http://localhost:3000.

### Test Production Build

**All Platforms:**
```bash
cd kit_playground
make playground
# or
python3 backend/web_server.py --port 8888 --open-browser
```

Should serve the production build and open in your browser.

---

## Build System Architecture

### Build Configuration

The build is configured in `package.json`:

```json
{
  "name": "kit-playground",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}
```

### What Gets Built

1. **React App** - Compiled JavaScript (~5MB)
2. **Python Backend** - Source files (~2MB)
3. **Templates + Tools** - Kit SDK tools (~50MB)
4. **Static Assets** - Images, CSS, etc. (~1MB)

**Total build size**: ~60MB

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

# Output: ui/build/ (production React build)
```

**Windows:**
```cmd
# From kit_playground directory
build.bat

REM Output: ui\build\ (production React build)
```

---

## Troubleshooting

### Issue: "react-scripts: command not found"

**Solution**: Install dependencies first
```bash
cd kit_playground/ui
npm install
```

### Issue: "Python backend fails to start"

**Solution**: Install Python dependencies
```bash
pip install -r backend/requirements.txt
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

      - name: Build React App
        run: |
          cd kit_playground/ui
          npm run build

      - name: Upload Build
        uses: actions/upload-artifact@v3
        with:
          name: kit-playground-build
          path: kit_playground/ui/build/
```

---

## Summary

**Recommended: Container Builds**
- **Requires on host:** Docker, Python, Git (NO Node.js needed!)
- **Command:** `make playground` or `make playground-build`
- **Works on:** Linux x86_64, Linux ARM64
- **Output:** `ui/build/` (~60MB production React build)

**Alternative: Native Builds**
- **Requires on host:** Node.js, npm, Python, Git
- **Command:** `./build.sh` (Linux) or `build.bat` (Windows)
- **Works on:** Linux x86_64, Linux ARM64, Windows x86_64
- **Output:** `ui/build/` (production React build)

**Key Points:**
- ✅ Container builds = no Node.js on host
- ✅ Both modes support x86_64 and ARM64
- ✅ Web-based application served by Flask backend
- ✅ All dependencies from public registries (npm, PyPI)