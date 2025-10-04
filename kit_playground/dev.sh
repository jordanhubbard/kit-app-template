#!/bin/bash
# Kit Playground Development Mode
# Runs backend and frontend with hot-reloading

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UI_DIR="$SCRIPT_DIR/ui"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is required for development mode${NC}"
    echo "Install: make install-npm"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is required${NC}"
    exit 1
fi

# Check if we have npm packages
if [ ! -d "$UI_DIR/node_modules" ]; then
    echo -e "${BLUE}Installing npm dependencies...${NC}"
    cd "$UI_DIR"
    npm install
    cd "$SCRIPT_DIR"
fi

# Determine host based on REMOTE environment variable
if [ "$REMOTE" = "1" ]; then
    BACKEND_HOST="0.0.0.0"
    FRONTEND_HOST="0.0.0.0"
    DISPLAY_HOST="0.0.0.0"
else
    BACKEND_HOST="localhost"
    FRONTEND_HOST="localhost"
    DISPLAY_HOST="localhost"
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Kit Playground - Development Mode with Hot Reload        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Starting services:${NC}"
echo -e "  • Backend API:  ${GREEN}http://${DISPLAY_HOST}:8081${NC}"
echo -e "  • Frontend UI:  ${GREEN}http://${DISPLAY_HOST}:3000${NC} ${YELLOW}(with hot-reload)${NC}"
if [ "$REMOTE" = "1" ]; then
    echo -e "  ${YELLOW}⚠ Remote mode: Listening on 0.0.0.0 (all interfaces)${NC}"
fi
echo ""
echo -e "${YELLOW}Changes to React/TypeScript files will hot-reload automatically!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup EXIT INT TERM

# Start backend in background
echo -e "${BLUE}[1/2] Starting Backend API server...${NC}"
cd "$BACKEND_DIR"
python3 web_server.py --port 8081 --host "$BACKEND_HOST" > /tmp/playground-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Backend failed to start. Check /tmp/playground-backend.log${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend running (PID: $BACKEND_PID)${NC}"

# Start frontend dev server
echo -e "${BLUE}[2/2] Starting React dev server with hot-reload...${NC}"
cd "$UI_DIR"
if [ "$REMOTE" = "1" ]; then
    BROWSER=none HOST="$FRONTEND_HOST" npm start &
else
    BROWSER=none npm start &
fi
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✓ Development servers are running!${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "  • View backend logs:  tail -f /tmp/playground-backend.log"
echo -e "  • Rebuild UI:         cd kit_playground/ui && npm run build"
echo ""

# Wait for both processes
wait
