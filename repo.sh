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

# Handle template new with template name argument
if [ "$1" = "template" ] && [ "$2" = "new" ] && [ "$#" -ge 3 ] && [ "$3" != "--generate-playback" ]; then
    TEMPLATE_NAME="$3"
    shift 3  # Remove 'template', 'new', and template_name from args

    # Extract additional arguments if provided
    APP_NAME=""
    DISPLAY_NAME=""
    VERSION=""

    while [ "$#" -gt 0 ]; do
        case "$1" in
            --name=*)
                APP_NAME="${1#*=}"
                ;;
            --display-name=*)
                DISPLAY_NAME="${1#*=}"
                ;;
            --version=*)
                VERSION="${1#*=}"
                ;;
            --name)
                shift
                APP_NAME="$1"
                ;;
            --display-name)
                shift
                DISPLAY_NAME="$1"
                ;;
            --version)
                shift
                VERSION="$1"
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done

    # Generate playbook file using helper script
    PLAYBACK_ARGS="$TEMPLATE_NAME"
    [ -n "$APP_NAME" ] && PLAYBACK_ARGS="$PLAYBACK_ARGS $APP_NAME"
    [ -n "$DISPLAY_NAME" ] && PLAYBACK_ARGS="$PLAYBACK_ARGS $DISPLAY_NAME"
    [ -n "$VERSION" ] && PLAYBACK_ARGS="$PLAYBACK_ARGS $VERSION"

    PLAYBACK_FILE=$("${OMNI_REPO_ROOT}/tools/packman/python.sh" "${OMNI_REPO_ROOT}/tools/repoman/template_helper.py" $PLAYBACK_ARGS)

    if [ $? -ne 0 ]; then
        exit 1
    fi

    # Run template replay with generated playback file
    exec "${OMNI_REPO_ROOT}/tools/packman/python.sh" "${OMNI_REPO_ROOT}/tools/repoman/repoman.py" template replay "$PLAYBACK_FILE"
else
    # Use "exec" to ensure that environment variables don't accidentally affect other processes.
    exec "${OMNI_REPO_ROOT}/tools/packman/python.sh" "${OMNI_REPO_ROOT}/tools/repoman/repoman.py" "$@"
fi
