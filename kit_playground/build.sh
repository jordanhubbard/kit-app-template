#!/bin/bash
# Build Kit Playground for Linux

set -e

echo "======================================"
echo "Kit Playground Build Script"
echo "======================================"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ first."
    echo "   Run: make install-deps"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi

echo "✓ npm version: $(npm --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python version: $(python3 --version)"
echo ""

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
else
    echo "✓ npm dependencies already installed"
fi

# Install Python dependencies
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r backend/requirements.txt
else
    echo "✓ Python dependencies already installed"
fi

echo ""
echo "======================================"
echo "Building Production Distributable"
echo "======================================"
echo ""

# Build React app
echo "🔨 Building React app..."
npm run build

# Build Electron app
echo "🔨 Building Electron AppImage..."
npm run dist

echo ""
echo "======================================"
echo "✅ Build Complete!"
echo "======================================"
echo ""

if [ -f "dist/Kit Playground-1.0.0.AppImage" ]; then
    echo "📦 AppImage created:"
    ls -lh dist/*.AppImage
    echo ""
    echo "To run:"
    echo "  chmod +x \"dist/Kit Playground-1.0.0.AppImage\""
    echo "  ./\"dist/Kit Playground-1.0.0.AppImage\""
else
    echo "⚠️  AppImage not found in dist/"
    echo "Check for errors above."
fi