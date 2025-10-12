#!/bin/bash
# App-specific wrapper script for calling repository root repo.sh
# Automatically determines app name from current directory and passes it to launch

set -e

# Find repository root by looking for repo.sh and repo.toml
find_repo_root() {
    local dir="$PWD"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/repo.sh" ] && [ -f "$dir/repo.toml" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo "Error: Could not find repository root (looking for repo.sh and repo.toml)" >&2
    return 1
}

# Detect app name from current directory structure
# Assumes we're in source/apps/{app_name}/ or similar
detect_app_name() {
    local current_dir="$(basename "$PWD")"
    local parent_dir="$(basename "$(dirname "$PWD")")"
    
    # If we're in source/apps/{app_name}, use {app_name}
    if [ "$parent_dir" = "apps" ]; then
        echo "$current_dir"
        return 0
    fi
    
    # Otherwise, try to find .kit file in current directory
    local kit_file=$(ls *.kit 2>/dev/null | head -1)
    if [ -n "$kit_file" ]; then
        # Strip .kit extension to get app name
        echo "${kit_file%.kit}"
        return 0
    fi
    
    # Fallback: use directory name
    echo "$current_dir"
}

REPO_ROOT=$(find_repo_root)
if [ $? -ne 0 ]; then
    exit 1
fi

# Check if this is a 'launch' command without explicit --name argument
if [ "$1" = "launch" ] && ! [[ " $@ " =~ " --name " ]]; then
    APP_NAME=$(detect_app_name)
    
    # If we detected an app name and there's a .kit file for it, add --name automatically
    if [ -f "${APP_NAME}.kit" ] || [ -f "$REPO_ROOT/_build/linux-x86_64/release/${APP_NAME}.kit.sh" ]; then
        echo "Auto-detected app: ${APP_NAME}.kit"
        # Insert --name argument after 'launch'
        exec "$REPO_ROOT/repo.sh" launch --name "${APP_NAME}.kit" "${@:2}"
    fi
fi

# For all other commands, or if auto-detection failed, just pass through
exec "$REPO_ROOT/repo.sh" "$@"


