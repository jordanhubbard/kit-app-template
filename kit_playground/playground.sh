#!/bin/bash
# Kit Playground Launcher Script for Linux/Mac
# This script builds the UI and launches the Kit Playground web interface

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UI_DIR="$SCRIPT_DIR/ui"
BACKEND_DIR="$SCRIPT_DIR/backend"
BUILD_DIR="$UI_DIR/build"

echo -e "${BLUE}Kit Playground Launcher${NC}"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3 from: https://www.python.org/downloads/"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 is installed${NC}"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓ Node.js is installed${NC}"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi
echo -e "${GREEN}✓ npm is installed${NC}"

# Install Python dependencies
echo ""
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip3 install -r "$BACKEND_DIR/../backend/requirements.txt" --quiet

# Check if build exists
if [ ! -d "$BUILD_DIR" ]; then
    echo ""
    echo -e "${YELLOW}UI build not found. Building...${NC}"
    cd "$UI_DIR"
    npm install
    npm run build
    cd "$SCRIPT_DIR"
fi

# Launch the server
echo ""
echo -e "${GREEN}Launching Kit Playground...${NC}"
echo -e "${BLUE}The web interface will open in your default browser${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

python3 "$BACKEND_DIR/web_server.py" --port 8081 --open-browser
