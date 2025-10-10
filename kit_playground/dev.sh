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

# Find available ports dynamically
echo -e "${BLUE}Finding available ports...${NC}"
PORTS=$(python3 "$SCRIPT_DIR/find_free_port.py" 2 8000)
BACKEND_PORT=$(echo $PORTS | cut -d' ' -f1)
FRONTEND_PORT=$(echo $PORTS | cut -d' ' -f2)

if [ -z "$BACKEND_PORT" ] || [ -z "$FRONTEND_PORT" ]; then
    echo -e "${RED}✗ Failed to find available ports${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Allocated ports: Backend=$BACKEND_PORT, Frontend=$FRONTEND_PORT${NC}"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Kit Playground - Development Mode with Hot Reload        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Starting services:${NC}"
echo -e "  • Backend API:  ${GREEN}http://${DISPLAY_HOST}:${BACKEND_PORT}${NC} ${YELLOW}(with hot-reload)${NC}"
echo -e "  • Frontend UI:  ${GREEN}http://${DISPLAY_HOST}:${FRONTEND_PORT}${NC} ${YELLOW}(with hot-reload)${NC}"
if [ "$REMOTE" = "1" ]; then
    echo -e "  ${YELLOW}⚠ Remote mode: Listening on 0.0.0.0 (all interfaces)${NC}"
fi
echo ""
echo -e "${YELLOW}Both frontend and backend will hot-reload on code changes!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    # Clean up generated proxy config
    rm -f "$UI_DIR/src/setupProxy.js"
    exit 0
}
trap cleanup EXIT INT TERM

# Start backend in background with hot-reload enabled
echo -e "${BLUE}[1/2] Starting Backend API server with hot-reload...${NC}"
cd "$BACKEND_DIR"
python3 web_server.py --port "$BACKEND_PORT" --host "$BACKEND_HOST" --debug > /tmp/playground-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Backend failed to start. Check /tmp/playground-backend.log${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend running (PID: $BACKEND_PID)${NC}"

# Create temporary setupProxy.js with dynamic backend port
cat > "$UI_DIR/src/setupProxy.js" << EOF
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:${BACKEND_PORT}',
      changeOrigin: true,
      logLevel: 'warn',
    })
  );
};
EOF

# Start frontend dev server
echo -e "${BLUE}[2/2] Starting React dev server with hot-reload...${NC}"
cd "$UI_DIR"
if [ "$REMOTE" = "1" ]; then
    BROWSER=none HOST="$FRONTEND_HOST" PORT="$FRONTEND_PORT" DANGEROUSLY_DISABLE_HOST_CHECK=true npm start &
else
    BROWSER=none PORT="$FRONTEND_PORT" npm start &
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
