#!/usr/bin/env python3
"""
Per-app dependency puller - handles pulling Kit SDK and dependencies to app-specific locations.

This module orchestrates packman to install dependencies to per-app _kit/ directories.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Add tools path for imports
tools_path = Path(__file__).parent
if str(tools_path) not in sys.path:
    sys.path.insert(0, str(tools_path))

from app_dependencies import (
    should_use_per_app_deps,
    get_app_deps_config,
    get_app_kit_path,
    list_apps_with_per_app_deps
)


def get_repo_root() -> Path:
    """Get repository root path."""
    return Path(__file__).parent.parent.parent


def get_packman_executable() -> Path:
    """Get path to packman executable."""
    repo_root = get_repo_root()

    # Check for Windows
    if sys.platform == 'win32':
        packman = repo_root / "tools" / "packman" / "packman.cmd"
    else:
        packman = repo_root / "tools" / "packman" / "packman"

    if not packman.exists():
        raise FileNotFoundError(f"Packman not found at {packman}")

    return packman


def get_kit_sdk_xml_template() -> Path:
    """Get the template kit-sdk.packman.xml file."""
    repo_root = get_repo_root()
    template = repo_root / "tools" / "deps" / "kit-sdk.packman.xml"
    if not template.exists():
        raise FileNotFoundError(f"Kit SDK template not found: {template}")
    return template


def generate_app_kit_xml(app_path: Path, config: Dict[str, Any]) -> Path:
    """
    Generate packman XML for app-specific Kit SDK.

    Uses the existing kit-sdk.packman.xml as a template and modifies
    the linkPath to point to the app-specific _kit directory.

    Args:
        app_path: Path to application directory
        config: App dependency configuration

    Returns:
        Path to generated XML file
    """
    app_name = app_path.name

    # Determine platform and build config
    if sys.platform == 'win32':
        platform_target = 'windows-x86_64'
        platform_target_abi = 'windows-x86_64'
    elif sys.platform == 'darwin':
        platform_target = 'mac-x86_64'
        platform_target_abi = 'mac-x86_64'
    else:
        platform_target = 'linux-x86_64'
        platform_target_abi = 'linux-x86_64'

    build_config = 'release'  # Default to release

    # Read the template kit-sdk.packman.xml
    template_file = get_kit_sdk_xml_template()
    xml_content = template_file.read_text()

    # Resolve template variables
    xml_content = xml_content.replace('${platform_target}', platform_target)
    xml_content = xml_content.replace('${platform_target_abi}', platform_target_abi)
    xml_content = xml_content.replace('${config}', build_config)

    # Modify the linkPath to point to app-specific _kit directory
    # After variable resolution, it will be something like:
    # linkPath="../../_build/linux-x86_64/release/kit"
    # We want: linkPath="_kit/kit"
    import re
    xml_content = re.sub(
        r'linkPath="[^"]*"',
        'linkPath="_kit/kit"',
        xml_content
    )

    # Update the dependency name to be app-specific
    xml_content = re.sub(
        r'name="kit_sdk_\w+"',
        f'name="kit_sdk_app_{app_name}"',
        xml_content
    )

    # Write to app dependencies dir
    deps_dir = app_path / "dependencies"
    xml_file = deps_dir / "kit-sdk-app.packman.xml"
    xml_file.write_text(xml_content)

    return xml_file


def copy_global_kit_to_app(app_path: Path, verbose: bool = False) -> bool:
    """
    Copy global Kit SDK to app-specific location.

    This is a fallback for development when packman pull fails
    due to unavailable package versions.

    Args:
        app_path: Path to application directory
        verbose: Print verbose output

    Returns:
        True if successful, False otherwise
    """
    import shutil

    repo_root = get_repo_root()

    # Find global Kit SDK
    if sys.platform == 'win32':
        platform = 'windows-x86_64'
    elif sys.platform == 'darwin':
        platform = 'mac-x86_64'
    else:
        platform = 'linux-x86_64'

    global_kit = repo_root / "_build" / platform / "release" / "kit"

    if not global_kit.exists():
        if verbose:
            print(f"  Global Kit SDK not found at {global_kit}")
        return False

    # Copy to app-specific location
    app_kit = get_app_kit_path(app_path) / "kit"
    app_kit.parent.mkdir(parents=True, exist_ok=True)

    if app_kit.exists():
        if verbose:
            print(f"  Removing existing app Kit SDK...")
        shutil.rmtree(app_kit)

    if verbose:
        print(f"  Copying global Kit SDK to app-specific location...")
        print(f"    From: {global_kit}")
        print(f"    To: {app_kit}")

    shutil.copytree(global_kit, app_kit, symlinks=True)

    if verbose:
        print(f"  ✓ Kit SDK copied successfully")

    return True


def pull_app_dependencies(app_path: Path, verbose: bool = False, fallback_copy: bool = True) -> bool:
    """
    Pull dependencies for a specific app using packman.

    Args:
        app_path: Path to application directory
        verbose: Print verbose output
        fallback_copy: If True, copy global Kit SDK on packman failure

    Returns:
        True if successful, False otherwise
    """
    if not should_use_per_app_deps(app_path):
        if verbose:
            print(f"App {app_path.name} does not use per-app dependencies")
        return False

    config = get_app_deps_config(app_path)
    if not config:
        print(f"Error: Could not load config for {app_path.name}", file=sys.stderr)
        return False

    if verbose:
        print(f"Pulling per-app dependencies for {app_path.name}...")
        print(f"  Kit SDK version: {config['kit_sdk']['version']}")

    # Get packman executable
    try:
        packman = get_packman_executable()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

    # Generate app-specific packman XML
    try:
        xml_file = generate_app_kit_xml(app_path, config)
        if verbose:
            print(f"  Generated XML: {xml_file}")
    except Exception as e:
        print(f"Error generating XML: {e}", file=sys.stderr)
        return False

    # Setup environment for per-app installation
    env = os.environ.copy()
    kit_path = get_app_kit_path(app_path)

    # Set packman environment variables for app-specific cache
    cache_strategy = config.get('cache', {}).get('strategy', 'isolated')
    if cache_strategy == 'isolated':
        # Use app-specific cache
        app_cache = kit_path / "cache"
        app_cache.mkdir(parents=True, exist_ok=True)
        env['PM_PACKAGES_ROOT'] = str(app_cache)
        if verbose:
            print(f"  Using isolated cache: {app_cache}")
    else:
        if verbose:
            print(f"  Using shared cache")

    # Change to app directory for packman to resolve relative paths correctly
    original_dir = Path.cwd()
    os.chdir(app_path)

    try:
        # Run packman pull
        cmd = [str(packman), "pull", str(xml_file.relative_to(app_path))]

        if verbose:
            print(f"  Running: {' '.join(cmd)}")
            print(f"  Working directory: {app_path}")

        result = subprocess.run(
            cmd,
            env=env,
            capture_output=not verbose,
            text=True
        )

        if result.returncode != 0:
            if verbose:
                print(f"  Packman pull failed (may be due to unavailable package version)")

            if fallback_copy:
                if verbose:
                    print(f"  Attempting fallback: copying global Kit SDK...")
                os.chdir(original_dir)  # Return to original dir for copy
                if copy_global_kit_to_app(app_path, verbose=verbose):
                    return True
                else:
                    if verbose:
                        print(f"  Fallback copy also failed")

            print(f"Error pulling dependencies for {app_path.name}", file=sys.stderr)
            return False

        if verbose:
            print(f"  ✓ Dependencies pulled successfully")
            print(f"  Kit SDK installed to: {kit_path / 'kit'}")

        return True

    except Exception as e:
        print(f"Error running packman: {e}", file=sys.stderr)
        return False
    finally:
        os.chdir(original_dir)


def pull_all_app_dependencies(repo_root: Optional[Path] = None, verbose: bool = False) -> int:
    """
    Pull dependencies for all apps that use per-app dependencies.

    Args:
        repo_root: Repository root path (auto-detected if None)
        verbose: Print verbose output

    Returns:
        Number of apps successfully processed
    """
    if repo_root is None:
        repo_root = get_repo_root()

    apps = list_apps_with_per_app_deps(repo_root)

    if not apps:
        if verbose:
            print("No apps with per-app dependencies found")
        return 0

    if verbose:
        print(f"Found {len(apps)} app(s) with per-app dependencies")
        print()

    success_count = 0
    for app_path in apps:
        if pull_app_dependencies(app_path, verbose=verbose):
            success_count += 1
        if verbose:
            print()

    if verbose:
        print(f"Successfully pulled dependencies for {success_count}/{len(apps)} app(s)")

    return success_count


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pull per-app dependencies for Kit applications"
    )
    parser.add_argument(
        "--app",
        help="Specific app name to pull dependencies for"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Pull dependencies for all apps with per-app deps"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    repo_root = get_repo_root()

    if args.app:
        # Pull for specific app
        app_path = repo_root / "source" / "apps" / args.app
        if not app_path.exists():
            print(f"Error: App not found: {app_path}", file=sys.stderr)
            return 1

        if pull_app_dependencies(app_path, verbose=args.verbose):
            return 0
        else:
            return 1

    elif args.all or not args.app:
        # Pull for all apps
        success_count = pull_all_app_dependencies(repo_root, verbose=args.verbose)
        return 0 if success_count > 0 else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
