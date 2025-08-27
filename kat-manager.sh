#!/bin/bash
# Kat Manager - Linux/macOS Entrypoint
# Cross-platform template system for Omniverse Kit applications and extensions

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Fast path commands - these try system Python first before setting up venv
FAST_PATH_COMMANDS="list schema"

# Function definitions first
show_help() {
    cat << EOF
Kat Manager - Modern Template System for Omniverse Kit

USAGE:
  kat-manager <command> [options]

TEMPLATE COMMANDS:
  list                     List available templates
  generate <template>      Generate from template
  schema <template>        Show template schema  
  validate <template>      Validate configuration

ENVIRONMENT COMMANDS:
  status                   Show environment status
  clean                    Remove virtual environment and generated content
  deploy <name> <path>     Deploy generated template to external location

EXAMPLES:
  kat-manager list
  kat-manager generate kit_base_editor -c config.yaml
  kat-manager deploy my_app /home/user/projects/
  kat-manager clean

For detailed help on template commands:
  kat-manager generate --help
  kat-manager schema --help
EOF
}

# Try fast path for read-only commands
try_fast_path() {
    local cmd="$1"
    shift
    
    # Check if this is a fast path command
    if echo "$FAST_PATH_COMMANDS" | grep -q "\b$cmd\b"; then
        # Try system Python first (capture output to avoid showing errors)
        if python3 "$SCRIPT_DIR/kat-manager" "$cmd" "$@" 2>/dev/null; then
            return 0
        fi
        # If fast path failed, fall back to full venv (will be tried by caller)
        return 1
    fi
    # Not a fast path command
    return 1
}

# Handle special commands
case "$1" in
    clean)
        echo "🧹 Cleaning Kat Manager environment..."
        python3 "$SCRIPT_DIR/kat_env_manager.py" clean
        exit $?
        ;;
    
    status)
        # Status is always fast since it doesn't need dependencies
        python3 "$SCRIPT_DIR/kat_env_manager.py" status
        exit $?
        ;;
    
    deploy)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "❌ Deploy command requires source name and target path"
            echo "Usage: kat-manager deploy <source_name> <target_path>"
            echo
            echo "Available templates:"
            python3 "$SCRIPT_DIR/kat_env_manager.py" list
            exit 1
        fi
        python3 "$SCRIPT_DIR/kat_env_manager.py" deploy --source "$2" --target "$3"
        exit $?
        ;;
    
    help|--help|-h|"")
        show_help
        exit 0
        ;;
    
    *)
        # Try fast path first for eligible commands
        if try_fast_path "$@"; then
            exit 0
        fi
        
        # Fall back to full venv setup for all commands (fast path failed or not applicable)
        python3 "$SCRIPT_DIR/kat_env_manager.py" run "$@"
        exit $?
        ;;
esac
