#!/bin/bash
# Cleanup script for removing partial/failed Kit project attempts
# Usage: ./cleanup-project.sh <project_name>

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$SCRIPT_DIR"

if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Project name required${NC}"
    echo ""
    echo "Usage: $0 <project_name>"
    echo ""
    echo "Examples:"
    echo "  $0 my_company.explorer"
    echo "  $0 my_app"
    exit 1
fi

PROJECT_NAME="$1"

echo -e "${BLUE}Kit Project Cleanup Tool${NC}"
echo ""
echo -e "${YELLOW}Project to clean: ${PROJECT_NAME}${NC}"
echo ""
echo -e "${YELLOW}This will remove all files related to this project${NC}"
echo ""
read -p "Are you sure? yes/no: " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Cleanup cancelled${NC}"
    exit 0
fi

echo -e "${BLUE}Starting cleanup...${NC}"
echo ""

# Remove from source/apps/
if [ -d "$REPO_ROOT/source/apps/$PROJECT_NAME" ]; then
    echo "Removing: source/apps/$PROJECT_NAME"
    rm -rf "$REPO_ROOT/source/apps/$PROJECT_NAME"
    echo -e "  ${GREEN}OK${NC}"
fi

# Remove setup extension
SETUP_EXT="${PROJECT_NAME}_setup"
if [ -d "$REPO_ROOT/source/extensions/$SETUP_EXT" ]; then
    echo "Removing: source/extensions/$SETUP_EXT"
    rm -rf "$REPO_ROOT/source/extensions/$SETUP_EXT"
    echo -e "  ${GREEN}OK${NC}"
fi

# Remove any extensions matching project name
for ext_dir in "$REPO_ROOT/source/extensions/${PROJECT_NAME}"*; do
    if [ -d "$ext_dir" ]; then
        echo "Removing: $ext_dir"
        rm -rf "$ext_dir"
        echo -e "  ${GREEN}OK${NC}"
    fi
done

# Remove from _build/apps/
if [ -d "$REPO_ROOT/_build/apps/$PROJECT_NAME" ]; then
    echo "Removing: _build/apps/$PROJECT_NAME"
    rm -rf "$REPO_ROOT/_build/apps/$PROJECT_NAME"
    echo -e "  ${GREEN}OK${NC}"
fi

# Remove .kit symlinks
if [ -L "$REPO_ROOT/_build/apps/${PROJECT_NAME}.kit" ]; then
    echo "Removing: _build/apps/${PROJECT_NAME}.kit"
    rm -f "$REPO_ROOT/_build/apps/${PROJECT_NAME}.kit"
    echo -e "  ${GREEN}OK${NC}"
fi

# Remove from build directories
for build_dir in "$REPO_ROOT/_build"/*/*/; do
    if [ -d "$build_dir" ]; then
        # Remove .kit files
        for file in "$build_dir"*"${PROJECT_NAME}"*.kit*; do
            if [ -e "$file" ]; then
                echo "Removing: $(basename "$file")"
                rm -f "$file"
                echo -e "  ${GREEN}OK${NC}"
            fi
        done

        # Remove test scripts
        for file in "$build_dir"tests-"${PROJECT_NAME}"*; do
            if [ -e "$file" ]; then
                echo "Removing: $(basename "$file")"
                rm -f "$file"
                echo -e "  ${GREEN}OK${NC}"
            fi
        done

        # Remove extensions
        if [ -d "$build_dir/exts" ]; then
            for ext_dir in "$build_dir/exts/${PROJECT_NAME}"* "$build_dir/exts/$SETUP_EXT"; do
                if [ -d "$ext_dir" ]; then
                    echo "Removing: exts/$(basename "$ext_dir")"
                    rm -rf "$ext_dir"
                    echo -e "  ${GREEN}OK${NC}"
                fi
            done
        fi
    fi
done

echo ""
echo -e "${GREEN}Cleanup Complete!${NC}"
echo ""
echo -e "${BLUE}Project ${PROJECT_NAME} has been completely removed${NC}"
echo -e "${BLUE}You can now create a new project with the same name${NC}"
echo ""
