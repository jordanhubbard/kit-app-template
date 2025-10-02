#!/bin/bash

set -e

# Set OMNI_REPO_ROOT early so `repo` bootstrapping can target the repository
# root when writing out Python dependencies.
export OMNI_REPO_ROOT="$( cd "$(dirname "$0")" ; pwd -P )"

# By default custom caching is disabled in repo_man. But if a repo-cache.json
# caching configuration file is generated via the `repo cache` command, it's
# presence will trigger the configuration of custom caching.
if [[ -f "${OMNI_REPO_ROOT}/repo-cache.json" ]]; then
    PM_PACKAGES_ROOT=$(grep '"PM_PACKAGES_ROOT"' "${OMNI_REPO_ROOT}/repo-cache.json" | sed 's/.*"PM_PACKAGES_ROOT": "\(.*\)".*/\1/')

    # PM_PACKAGES_ROOT is present in the config file. We set this early
    # so Packman will reference our cached package repository.
    if [[ -n "${PM_PACKAGES_ROOT}" ]]; then
        # Use eval to resolve ~ and perform parameter expansion
        RESOLVED_PACKAGES_ROOT=$(eval echo "$PM_PACKAGES_ROOT")

        if [[ "${RESOLVED_PACKAGES_ROOT}" != /* ]]; then
            # PM_PACKAGES_ROOT is not an abs path, assumption is then
            # that it is a relative path to the repository root.
            PM_PACKAGES_ROOT="${OMNI_REPO_ROOT}/${RESOLVED_PACKAGES_ROOT}"
        else
            PM_PACKAGES_ROOT=${RESOLVED_PACKAGES_ROOT}
        fi
        export PM_PACKAGES_ROOT
    fi
fi

# Check for special playground commands
case "$1" in
    playground)
        case "$2" in
            install|"")
                # Check for npm first
                if ! command -v npm >/dev/null 2>&1; then
                    echo "ERROR: npm is not installed. Please install Node.js first."
                    echo ""
                    echo "Run: make install-deps"
                    echo "Or install manually from: https://nodejs.org/en/download/"
                    exit 1
                fi

                if [ "$2" = "install" ]; then
                    echo "Installing Kit Playground dependencies..."
                    cd "${OMNI_REPO_ROOT}/kit_playground" && npm install
                else
                    # Check if dependencies are installed
                    if [ ! -d "${OMNI_REPO_ROOT}/kit_playground/node_modules" ]; then
                        echo "Kit Playground dependencies not installed. Installing first..."
                        cd "${OMNI_REPO_ROOT}/kit_playground" && npm install
                    fi
                    echo "Launching Kit Playground..."
                    cd "${OMNI_REPO_ROOT}/kit_playground" && npm start
                fi
                ;;
            dev)
                echo "Starting Kit Playground in development mode..."
                cd "${OMNI_REPO_ROOT}/kit_playground" && npm run dev
                ;;
            build)
                echo "Building Kit Playground for production..."
                cd "${OMNI_REPO_ROOT}/kit_playground" && npm run build
                ;;
            *)
                echo "Unknown playground command: $2"
                echo "Available commands: install, dev, build"
                exit 1
                ;;
        esac
        ;;
    playground-install)
        exec "$0" playground install
        ;;
    playground-dev)
        exec "$0" playground dev
        ;;
    playground-build)
        exec "$0" playground build
        ;;
    *)
        # Check and install required Python dependencies (first run only)
        "${OMNI_REPO_ROOT}/tools/packman/python.sh" "${OMNI_REPO_ROOT}/tools/repoman/check_dependencies.py" || {
            echo "Failed to verify Python dependencies. Some commands may not work." >&2
        }

        # Default: Use the Python dispatcher for enhanced template functionality and fallback to repoman
        exec "${OMNI_REPO_ROOT}/tools/packman/python.sh" "${OMNI_REPO_ROOT}/tools/repoman/repo_dispatcher.py" "$@"
        ;;
esac