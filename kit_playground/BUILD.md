# Kit Playground - Build Instructions

## Overview

Kit Playground is an Electron application that can be built natively on Linux, macOS, and Windows. It does **NOT** require Docker for building or running - all dependencies are installed via npm and pip.

## System Requirements

### Linux (Current System: Ubuntu 22.04 x86_64)
- Node.js 16+ and npm 7+
- Python 3.8+
- Git
- Standard build tools: `build-essential` (for native npm modules)

### Additional for Building AppImage
- FUSE 2 (for running AppImage)
- `libgtk-3-0` and `libnotify4` (GTK dependencies)

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

### Build for Current Platform (Linux AppImage)

```bash
cd kit_playground

# First, install dependencies if not already done
npm install

# Build the React app
npm run build

# Build Electron distributable for Linux
npm run dist
```

This creates: `dist/Kit Playground-1.0.0.AppImage`

### Build for All Platforms

```bash
npm run dist:all
```

This creates:
- **Linux**: `dist/Kit Playground-1.0.0.AppImage`
- **macOS**: `dist/Kit Playground-1.0.0.dmg` (requires macOS to sign)
- **Windows**: `dist/Kit Playground Setup 1.0.0.exe` (requires Wine on Linux)

**Note**: Cross-platform builds from Linux have limitations:
- macOS builds cannot be signed without macOS
- Windows builds work but may require Wine for best results

---

## Build Output Structure

After `npm run dist`, you'll find:

```
kit_playground/
├── build/              # Compiled React app (npm run build)
│   └── index.html
├── dist/               # Electron distributables (npm run dist)
│   ├── Kit Playground-1.0.0.AppImage     # Linux
│   ├── Kit Playground-1.0.0.dmg          # macOS (if built on macOS)
│   └── Kit Playground Setup 1.0.0.exe    # Windows (if built on Windows)
└── node_modules/       # Dependencies
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

## Docker Usage (Optional)

The project does **NOT** require Docker for building, but you can use it if preferred:

### Create Dockerfile for Building

```dockerfile
FROM node:18-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    build-essential \
    libgtk-3-0 libnotify4 libnss3 libxss1 \
    fuse libfuse2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY kit_playground/package*.json ./
RUN npm install

# Copy source
COPY kit_playground/ ./
COPY tools/ ../tools/
COPY templates/ ../templates/

# Install Python deps
RUN pip3 install -r backend/requirements.txt

# Build
RUN npm run build
RUN npm run dist

CMD ["npm", "start"]
```

### Build in Docker

```bash
cd /home/jkh/Src/kit-app-template

# Build Docker image
docker build -f kit_playground/Dockerfile -t kit-playground-builder .

# Extract AppImage
docker run --rm -v $(pwd)/dist:/output kit-playground-builder \
    cp /app/dist/*.AppImage /output/
```

**But this is NOT necessary** - native builds work fine!

---

## Testing the Build

### Test Development Build

```bash
cd kit_playground
npm start
```

Should open the Electron app with all features working.

### Test Production AppImage (Linux)

```bash
cd kit_playground/dist

# Make executable
chmod +x "Kit Playground-1.0.0.AppImage"

# Run
./"Kit Playground-1.0.0.AppImage"
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

## Current System Compatibility

### ✅ Your Linux Machine WILL Build Successfully

- **OS**: Ubuntu 22.04.5 LTS ✅
- **Arch**: x86_64 ✅
- **Docker**: Installed (optional) ✅
- **Node.js**: Required (install with `make install-deps`) ✅
- **Python**: Already available ✅

### Build Commands That Will Work

```bash
# Install all deps
make install-deps

# Install Kit Playground deps
cd kit_playground && npm install && pip install -r backend/requirements.txt

# Build for Linux
npm run dist

# Output: dist/Kit Playground-1.0.0.AppImage
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

**Does it need Docker?** ❌ No - builds natively
**Will it build on your Linux machine?** ✅ Yes - Ubuntu 22.04 x86_64 fully supported
**How are dependencies installed?** Via `npm install` (public registry) and `pip install` (PyPI)
**Build command?** `npm run dist` creates AppImage
**Output?** `dist/Kit Playground-1.0.0.AppImage` (~350MB)

The build process is **completely standalone** and does not require any NVIDIA-internal infrastructure or Docker containers!