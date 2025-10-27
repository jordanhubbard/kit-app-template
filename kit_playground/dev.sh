#!/bin/bash
# Kit Playground Development Mode
# Runs backend API and frontend UI with hot-reloading

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
    echo -e "${BLUE}Installing UI dependencies...${NC}"
    cd "$UI_DIR"
    npm install
    cd "$SCRIPT_DIR"
fi

# Fixed ports for simplicity
BACKEND_PORT=5000
FRONTEND_PORT=3000

# Determine host based on REMOTE environment variable
if [ "$REMOTE" = "1" ]; then
    export REMOTE=1  # Ensure REMOTE is exported for child processes (Vite)
    BACKEND_HOST="0.0.0.0"  # Bind to all interfaces
    FRONTEND_HOST="0.0.0.0"  # Bind to all interfaces

    # For remote mode, use the actual IP address for client connections
    # Try to get the IP address used for external connections
    ACTUAL_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[0-9.]+' || hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

    DISPLAY_HOST="${ACTUAL_IP}"
    # For API URLs, use the actual IP so browser can connect remotely
    API_HOST="${ACTUAL_IP}"
else
    export REMOTE=0  # Explicitly set to 0 for local mode
    BACKEND_HOST="localhost"
    FRONTEND_HOST="localhost"
    DISPLAY_HOST="localhost"
    API_HOST="localhost"
fi

# Determine mode
if [ "$PRODUCTION" = "1" ] || [ "$PRODUCTION" = "yes" ] || [ "$PRODUCTION" = "true" ]; then
    MODE="Production"
    MODE_COLOR="${RED}"
else
    MODE="Development"
    MODE_COLOR="${GREEN}"
fi

echo -e "${MODE_COLOR}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MODE_COLOR}║  Kit App Template Playground - ${MODE} Mode                ║${NC}"
echo -e "${MODE_COLOR}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo -e "  ${GREEN}✓${NC} Backend API:  ${GREEN}http://${DISPLAY_HOST}:${BACKEND_PORT}${NC}"
echo -e "  ${GREEN}✓${NC} Frontend UI:  ${GREEN}http://${DISPLAY_HOST}:${FRONTEND_PORT}${NC}"
echo -e "  ${GREEN}✓${NC} API Docs:     ${GREEN}http://${DISPLAY_HOST}:${BACKEND_PORT}/api/docs${NC}"
if [ "$REMOTE" = "1" ]; then
    echo -e "  ${YELLOW}⚠${NC} Remote mode: Listening on 0.0.0.0 (all interfaces)"
fi
echo ""
if [ "$PRODUCTION" = "1" ] || [ "$PRODUCTION" = "yes" ] || [ "$PRODUCTION" = "true" ]; then
    echo -e "${BLUE}Production build - optimized for performance${NC}"
else
    echo -e "${YELLOW}Development mode - hot-reload enabled${NC}"
fi
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    # Kill any remaining processes on our ports
    lsof -ti:$BACKEND_PORT 2>/dev/null | xargs -r kill -9 2>/dev/null || true
    lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs -r kill -9 2>/dev/null || true
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}
trap cleanup EXIT INT TERM

# Start backend in background
echo -e "${BLUE}Starting backend API on port ${BACKEND_PORT}...${NC}"
cd "$BACKEND_DIR"
if [ "$PRODUCTION" = "1" ] || [ "$PRODUCTION" = "yes" ] || [ "$PRODUCTION" = "true" ]; then
    python3 web_server.py --port "$BACKEND_PORT" --host "$BACKEND_HOST" > /tmp/kit-playground-backend.log 2>&1 &
else
    python3 web_server.py --port "$BACKEND_PORT" --host "$BACKEND_HOST" --debug > /tmp/kit-playground-backend.log 2>&1 &
fi
BACKEND_PID=$!

# Wait for backend to start with proper health check
echo -n "Waiting for backend to be ready"
BACKEND_READY=0
for i in {1..30}; do
    # Check if process is still alive
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "\n${RED}✗ Backend process died. Check /tmp/kit-playground-backend.log${NC}"
        tail -50 /tmp/kit-playground-backend.log
        exit 1
    fi

    # Check if backend is responding to HTTP requests
    if curl -s -f http://localhost:${BACKEND_PORT}/api/health > /dev/null 2>&1; then
        BACKEND_READY=1
        break
    fi

    echo -n "."
    sleep 1
done

echo "" # newline

if [ $BACKEND_READY -eq 0 ]; then
    echo -e "${RED}✗ Backend failed to become ready after 30 seconds${NC}"
    echo -e "${YELLOW}Last 50 lines of backend log:${NC}"
    tail -50 /tmp/kit-playground-backend.log
    exit 1
fi

echo -e "${GREEN}✓ Backend started and ready (PID: $BACKEND_PID)${NC}"

# Start frontend with Vite
echo -e "${BLUE}Starting frontend UI on port ${FRONTEND_PORT}...${NC}"
cd "$UI_DIR"

# Set environment variables for Vite
# Use API_HOST (actual hostname) for client connections, not BACKEND_HOST (bind address)
export VITE_API_BASE_URL="http://${API_HOST}:${BACKEND_PORT}/api"
export VITE_WS_BASE_URL="http://${API_HOST}:${BACKEND_PORT}"

if [ "$PRODUCTION" = "1" ] || [ "$PRODUCTION" = "yes" ] || [ "$PRODUCTION" = "true" ]; then
    # Production mode: build and preview
    npm run build > /tmp/kit-playground-frontend.log 2>&1
    if [ "$REMOTE" = "1" ]; then
        npm run preview -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" > /tmp/kit-playground-frontend.log 2>&1 &
    else
        npm run preview -- --port "$FRONTEND_PORT" > /tmp/kit-playground-frontend.log 2>&1 &
    fi
else
    # Development mode: hot-reload with Vite
    if [ "$REMOTE" = "1" ]; then
        npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" > /tmp/kit-playground-frontend.log 2>&1 &
    else
        npm run dev -- --port "$FRONTEND_PORT" > /tmp/kit-playground-frontend.log 2>&1 &
    fi
fi
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${BLUE}Waiting for UI to be ready...${NC}"
sleep 3

# Check if frontend is responding
# Note: Always use localhost for health check, even when binding to 0.0.0.0
# (0.0.0.0 is a bind address, not a connection address)
MAX_RETRIES=10
RETRY_COUNT=0
FRONTEND_READY=0
HEALTH_CHECK_URL="http://localhost:${FRONTEND_PORT}"
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
        FRONTEND_READY=1
        break
    fi
    sleep 1
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $FRONTEND_READY -eq 1 ]; then
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  All services running!                                     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Access the UI at:${NC}     ${GREEN}http://${DISPLAY_HOST}:${FRONTEND_PORT}${NC}"
    echo -e "${BLUE}API documentation:${NC}    ${GREEN}http://${DISPLAY_HOST}:${BACKEND_PORT}/api/docs${NC}"
    echo ""
    echo -e "${YELLOW}Logs:${NC}"
    echo -e "  Backend:  /tmp/kit-playground-backend.log"
    echo -e "  Frontend: /tmp/kit-playground-frontend.log"
    echo ""
else
    echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
    echo -e "${YELLOW}Check: http://localhost:${FRONTEND_PORT}${NC}"
    echo -e "${YELLOW}Logs: /tmp/kit-playground-frontend.log${NC}"
fi

# Wait for processes (keeps script running)
wait
