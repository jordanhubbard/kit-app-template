#!/usr/bin/env python3
"""
Per-application dependency management for Kit App Template.

This module provides functionality for apps to have isolated Kit SDK and dependencies,
allowing different apps to use different Kit versions without conflicts.

Key Features:
- Per-app Kit SDK isolation
- Custom dependency versions per app
- Backward compatible (apps without config use global deps)
- Packman integration without core changes
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Handle TOML imports (Python 3.11+ has built-in tomllib)
try:
    import tomllib
    HAS_TOMLLIB = True
    try:
        import tomli_w
        HAS_TOMLI_W = True
    except ImportError:
        HAS_TOMLI_W = False
    HAS_TOML = True
except ImportError:
    HAS_TOMLLIB = False
    HAS_TOMLI_W = False
    HAS_TOML = True


def load_toml(file_path: Path) -> Dict[str, Any]:
    """
    Load TOML configuration file.

    Args:
        file_path: Path to TOML file

    Returns:
        Dictionary with configuration data

    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: If TOML parsing fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    if HAS_TOMLLIB:
        with open(file_path, 'rb') as f:
            return tomllib.load(f)
    elif HAS_TOML:
        import toml as toml_lib
        with open(file_path, 'r', encoding='utf-8') as f:
            return toml_lib.load(f)
    else:
        raise RuntimeError("No TOML library available")


def write_toml(file_path: Path, data: Dict[str, Any]) -> None:
    """
    Write TOML configuration file.

    Args:
        file_path: Path to write TOML file
        data: Dictionary to write as TOML
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if HAS_TOMLI_W:
        with open(file_path, 'wb') as f:
            tomli_w.dump(data, f)
    elif HAS_TOML:
        import toml as toml_lib
        with open(file_path, 'w', encoding='utf-8') as f:
            toml_lib.dump(data, f)
    else:
        raise RuntimeError("No TOML writing library available")


def should_use_per_app_deps(app_path: Path) -> bool:
    """
    Check if an application should use per-app dependencies.

    An app uses per-app dependencies if it has a dependencies/ directory
    with a kit-deps.toml configuration file.

    Args:
        app_path: Path to application directory

    Returns:
        True if app should use per-app dependencies, False otherwise
    """
    if not app_path or not app_path.exists():
        return False

    deps_dir = app_path / "dependencies"
    deps_config = deps_dir / "kit-deps.toml"

    return deps_dir.exists() and deps_config.exists()


def get_app_deps_config(app_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load app-specific dependency configuration.

    Args:
        app_path: Path to application directory

    Returns:
        Dictionary with dependency configuration, or None if not configured
    """
    if not should_use_per_app_deps(app_path):
        return None

    config_file = app_path / "dependencies" / "kit-deps.toml"
    try:
        return load_toml(config_file)
    except Exception as e:
        msg = "Warning: Failed to load dependency config from "
        msg += f"{config_file}: {e}"
        print(msg, file=sys.stderr)
        return None


def get_app_kit_path(app_path: Path) -> Path:
    """
    Get the Kit SDK installation path for an application.

    Args:
        app_path: Path to application directory

    Returns:
        Path where Kit SDK should be installed for this app
    """
    return app_path / "_kit"


def get_app_kit_executable(
    app_path: Path, platform: str = None
) -> Optional[Path]:
    """
    Find the Kit executable for a specific application.

    Args:
        app_path: Path to application directory
        platform: Platform identifier (e.g., 'linux-x86_64').
                  Auto-detected if None.

    Returns:
        Path to Kit executable if it exists, None otherwise
    """
    if platform is None:
        import platform as plat
        system = plat.system().lower()
        if system == 'windows':
            platform = 'windows-x86_64'
        elif system == 'linux':
            platform = 'linux-x86_64'
        else:
            platform = f'{system}-x86_64'

    # Check per-app Kit SDK
    app_kit_path = get_app_kit_path(app_path)
    kit_exe = app_kit_path / "kit" / "kit"

    if kit_exe.exists():
        return kit_exe

    # On Windows, check for .exe extension
    if 'windows' in platform.lower():
        kit_exe_win = app_kit_path / "kit" / "kit.exe"
        if kit_exe_win.exists():
            return kit_exe_win

    return None


def get_kit_sdk_version(app_path: Path) -> Optional[str]:
    """
    Get the Kit SDK version configured for an application.

    Args:
        app_path: Path to application directory

    Returns:
        Kit SDK version string, or None if not configured
    """
    config = get_app_deps_config(app_path)
    if config and 'kit_sdk' in config:
        return config['kit_sdk'].get('version')
    return None


def create_default_deps_config(
    kit_version: str = "106.0"
) -> Dict[str, Any]:
    """
    Create a default per-app dependency configuration.

    Args:
        kit_version: Kit SDK version to configure

    Returns:
        Dictionary with default configuration
    """
    return {
        "kit_sdk": {
            "version": kit_version
        },
        "cache": {
            "strategy": "isolated"
        },
        "dependencies": {}
    }


def initialize_per_app_deps(
    app_path: Path, kit_version: str = "106.0"
) -> bool:
    """
    Initialize per-app dependencies for an application.

    Creates the dependencies/ directory and kit-deps.toml configuration.

    Args:
        app_path: Path to application directory
        kit_version: Kit SDK version to configure

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        deps_dir = app_path / "dependencies"
        deps_dir.mkdir(parents=True, exist_ok=True)

        config_file = deps_dir / "kit-deps.toml"
        if not config_file.exists():
            config = create_default_deps_config(kit_version)
            write_toml(config_file, config)
            return True

        return True
    except Exception as e:
        msg = f"Error: Failed to initialize per-app dependencies: {e}"
        print(msg, file=sys.stderr)
        return False


def validate_deps_config(
    config: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """
    Validate per-app dependency configuration.

    Args:
        config: Configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(config, dict):
        return False, "Configuration must be a dictionary"

    # Check for required kit_sdk section
    if 'kit_sdk' not in config:
        return False, "Missing required 'kit_sdk' section"

    kit_sdk = config['kit_sdk']
    if not isinstance(kit_sdk, dict):
        return False, "'kit_sdk' must be a dictionary"

    # Check for required version
    if 'version' not in kit_sdk:
        return False, "Missing required 'kit_sdk.version'"

    version = kit_sdk['version']
    if not isinstance(version, str) or not version.strip():
        return False, "'kit_sdk.version' must be a non-empty string"

    # Validate cache strategy if present
    if 'cache' in config:
        cache = config['cache']
        if isinstance(cache, dict) and 'strategy' in cache:
            strategy = cache['strategy']
            if strategy not in ['isolated', 'shared']:
                msg = (f"Invalid cache strategy '{strategy}'. "
                       f"Must be 'isolated' or 'shared'")
                return False, msg

    return True, None


def get_app_name_from_path(app_path: Path) -> str:
    """
    Extract application name from path.

    Args:
        app_path: Path to application directory

    Returns:
        Application name (directory name)
    """
    return app_path.name


def get_app_path_from_name(repo_root: Path, app_name: str) -> Path:
    """
    Get application path from app name.

    Args:
        repo_root: Repository root path
        app_name: Application name

    Returns:
        Path to application directory
    """
    return repo_root / "source" / "apps" / app_name


def list_apps_with_per_app_deps(repo_root: Path) -> list[Path]:
    """
    List all applications that use per-app dependencies.

    Args:
        repo_root: Repository root path

    Returns:
        List of paths to apps with per-app dependencies
    """
    apps_dir = repo_root / "source" / "apps"
    if not apps_dir.exists():
        return []

    apps_with_deps = []
    for app_path in apps_dir.iterdir():
        if app_path.is_dir() and should_use_per_app_deps(app_path):
            apps_with_deps.append(app_path)

    return apps_with_deps
