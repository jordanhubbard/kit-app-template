#!/bin/bash
# Kit Playground Launcher Script for Linux/Mac
# DEPRECATED: Use 'make playground' instead
#
# This script is kept for backwards compatibility but now just
# launches development mode with hot-reload (the recommended way)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  Note: playground.sh is deprecated                        ║${NC}"
echo -e "${YELLOW}║  Use 'make playground' for the recommended workflow       ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Launching Kit Playground in development mode...${NC}"
echo ""

# Just run dev.sh
exec "$SCRIPT_DIR/dev.sh"
