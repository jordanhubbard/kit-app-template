#!/bin/bash
# Wrapper script to call repository root repo.sh from any app directory
# Automatically finds the repository root by walking up the directory tree

set -e

# Find repository root by looking for repo.sh or repo.toml
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

REPO_ROOT=$(find_repo_root)
if [ $? -ne 0 ]; then
    exit 1
fi

# Call the main repo.sh with all arguments
exec "$REPO_ROOT/repo.sh" "$@"
