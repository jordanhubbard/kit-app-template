#!/usr/bin/env python3
"""
OS-independent repo command dispatcher.
Handles enhanced template functionality and delegates other commands to repoman.
"""

import os
import sys
import shutil
import platform
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

def get_repo_root() -> Path:
    """Get the repository root directory."""
    # Find repo root by looking for repo.toml
    current_dir = Path(__file__).parent
    while current_dir.parent != current_dir:
        if (current_dir / "repo.toml").exists():
            return current_dir
        current_dir = current_dir.parent

    # Fallback: assume standard structure
    return Path(__file__).parent / ".." / ".."

def get_platform_info() -> Tuple[str, str]:
    """
    Get current platform and architecture.

    Returns:
        Tuple of (platform_name, architecture) matching build system conventions
        Examples: ('linux', 'x86_64'), ('windows', 'x86_64'), ('linux', 'aarch64')
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize platform name
    if system == 'darwin':
        platform_name = 'macos'
    elif system == 'windows':
        platform_name = 'windows'
    else:
        platform_name = 'linux'

    # Normalize architecture
    if machine in ['x86_64', 'amd64']:
        arch = 'x86_64'
    elif machine in ['aarch64', 'arm64']:
        arch = 'aarch64'
    elif machine in ['i386', 'i686']:
        arch = 'x86'
    else:
        arch = machine

    return platform_name, arch

def get_platform_build_dir(repo_root: Path, config: str = 'release') -> Path:
    """
    Get the platform-specific build directory.

    Args:
        repo_root: Repository root directory
        config: Build configuration (release or debug)

    Returns:
        Path to platform-specific build directory
        Example: /path/to/repo/_build/linux-x86_64/release
    """
    platform_name, arch = get_platform_info()
    return repo_root / "_build" / f"{platform_name}-{arch}" / config

def parse_template_new_args(args: List[str]) -> tuple[str, Dict[str, str], List[str]]:
    """Parse template new command arguments."""
    if len(args) < 3 or args[0] != "template" or args[1] != "new":
        raise ValueError("Expected 'template new <template_name>' format")

    template_name = args[2]
    kwargs = {}
    remaining_args = []

    i = 3
    while i < len(args):
        arg = args[i]

        if arg.startswith("--"):
            if "=" in arg:
                # Handle --key=value format
                key, value = arg[2:].split("=", 1)
                kwargs[key.replace("-", "_")] = value
            elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                # Handle --key value format
                key = arg[2:].replace("-", "_")
                kwargs[key] = args[i + 1]
                i += 1
            else:
                # Flag without value - keep as remaining arg
                remaining_args.append(arg)
        else:
            remaining_args.append(arg)

        i += 1

    return template_name, kwargs, remaining_args

def _fix_application_structure(repo_root: Path, playback_data: Dict[str, Any], build_config: str = 'release') -> None:
    """
    Fix application directory structure after template replay.

    The template replay system creates app.kit as a FILE in source/apps/,
    but we need it to be source/apps/{name}/{name}.kit (directory structure).
    The build system will then symlink source/apps → _build/{platform}/{config}/apps

    Args:
        repo_root: Repository root directory
        playback_data: Parsed playback TOML data
        build_config: Build configuration (release or debug), defaults to release
    """
    platform_name, arch = get_platform_info()

    # Determine if this is an application template
    # Application templates have 'application_name' or 'application_display_name'
    for template_name, config_data in playback_data.items():
        if template_name.startswith('_'):
            continue  # Skip internal fields like _standalone_project

        app_name = config_data.get('application_name')
        if not app_name:
            # Not an application, skip (might be extension)
            continue

        # Check if .kit file exists in source/apps (where omni.repo.man creates it)
        old_kit_file = repo_root / "source" / "apps" / f"{app_name}.kit"
        if not old_kit_file.exists():
            # File not found, might already be structured correctly or error occurred
            continue

        if old_kit_file.is_dir():
            # Already a directory, skip
            continue

        # Found a .kit FILE that should be restructured into a directory
        print(f"\nRestructuring application: {app_name}")
        print(f"Creating directory structure in source/apps/...")

        # Create new directory structure in source/apps
        # The build system will symlink this to _build/{platform}/{config}/apps
        app_dir = repo_root / "source" / "apps" / app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        # Move the .kit file into the directory
        new_kit_file = app_dir / f"{app_name}.kit"
        shutil.move(str(old_kit_file), str(new_kit_file))

        # Copy README.md from template if it exists
        template_readme = repo_root / "templates" / "apps" / template_name / "README.md"
        if template_readme.exists():
            shutil.copy2(str(template_readme), str(app_dir / "README.md"))

        # Create .project-meta.toml with metadata
        metadata_content = f"""# Project Metadata
# Auto-generated by Kit App Template System

[project]
name = "{app_name}"
display_name = "{config_data.get('application_display_name', app_name)}"
version = "{config_data.get('version', '0.1.0')}"
type = "application"
template = "{template_name}"
created = "{__import__('datetime').datetime.now().isoformat()}"

[build]
platforms = ["windows", "linux"]
config_file = "{app_name}.kit"
build_dir = "_build"

[files]
main_config = "{app_name}.kit"
readme = "README.md"
"""

        metadata_file = app_dir / ".project-meta.toml"
        metadata_file.write_text(metadata_content)

        # Create wrapper script that finds repo root and calls main repo.sh
        wrapper_script = app_dir / "repo.sh"
        wrapper_content = """#!/bin/bash
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
"""
        wrapper_script.write_text(wrapper_content)
        import os
        os.chmod(str(wrapper_script), 0o755)  # Make executable

        # Create Windows batch wrapper
        wrapper_bat = app_dir / "repo.bat"
        wrapper_bat_content = """@echo off
REM Wrapper script to call repository root repo.bat from any app directory
REM Automatically finds the repository root by walking up the directory tree

setlocal enabledelayedexpansion

:find_repo_root
set "current_dir=%CD%"

:loop
if exist "%current_dir%\\repo.bat" (
    if exist "%current_dir%\\repo.toml" (
        set "REPO_ROOT=%current_dir%"
        goto found
    )
)

REM Go up one directory
for %%I in ("%current_dir%\\..") do set "current_dir=%%~fI"

REM Check if we reached the root
if "%current_dir%"=="%current_dir:~0,3%" (
    echo Error: Could not find repository root (looking for repo.bat and repo.toml) 1>&2
    exit /b 1
)

goto loop

:found
REM Call the main repo.bat with all arguments
call "%REPO_ROOT%\\repo.bat" %*
exit /b %ERRORLEVEL%
"""
        wrapper_bat.write_text(wrapper_bat_content)

        print(f"✓ Application '{app_name}' created successfully in")
        print(f"  {app_dir}")
        print("")
        print(f"Main configuration: {app_name}.kit")
        print("")
        print(f"To build (from repository root):")
        print(f"  cd {repo_root} && ./repo.sh build --config {build_config}")
        print("")
        print(f"Or build from app directory:")
        print(f"  cd {app_dir} && ./repo.sh build --config {build_config}")
        print("")
        print(f"Note: Build system will symlink to: _build/{platform_name}-{arch}/{build_config}/apps/{app_name}")
        print("")

        # Create the symlink immediately so UI can access files before first build
        # The build system will reuse this symlink if it already exists
        platform_build_dir = get_platform_build_dir(repo_root, build_config)
        symlink_path = platform_build_dir / "apps"
        symlink_target = repo_root / "source" / "apps"

        # Create symlink if it doesn't exist
        if not symlink_path.exists():
            symlink_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                symlink_path.symlink_to(symlink_target)
                print(f"✓ Created symlink: {symlink_path} → {symlink_target}")
            except Exception as e:
                logger.warning(f"Could not create symlink (build system will create it): {e}")
        elif symlink_path.is_symlink():
            print(f"✓ Symlink already exists: {symlink_path} → {symlink_path.readlink()}")
        else:
            logger.warning(f"Path exists but is not a symlink: {symlink_path}")

        # Fix repo.toml: The template replay adds entries with flat paths
        # (e.g., "source/apps/app.kit") but we've restructured to nested paths
        # (e.g., "source/apps/app/app.kit"). Since we use dynamic discovery
        # via app_discovery_paths, clear the static apps list to prevent build errors.
        try:
            import re
            repo_toml_path = repo_root / "repo.toml"
            if repo_toml_path.exists():
                content = repo_toml_path.read_text()
                
                # Use regex to clear the apps list without reformatting the file
                # This preserves comments and formatting
                pattern = r'^apps\s*=\s*\[.*?\]'
                replacement = 'apps = []'
                new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
                
                if count > 0:
                    repo_toml_path.write_text(new_content)
                    print(f"✓ Cleared static apps list in repo.toml (using dynamic discovery)")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Could not update repo.toml after restructuring: {e}")
            # Continue anyway - this is not critical as dynamic discovery should work

        # Return the new app directory path for API consumers
        return app_dir

def handle_template_command(args: List[str]) -> int:
    """Handle template commands with enhanced functionality."""
    repo_root = get_repo_root()

    if len(args) < 2:
        return call_repoman(args)

    subcommand = args[1]

    if subcommand == "new" and len(args) >= 3 and not args[2].startswith("--"):
        # Handle enhanced template new command
        try:
            template_name, kwargs, remaining_args = parse_template_new_args(args)

            # Build engine arguments
            engine_args = [template_name]

            # Add all kwargs as arguments (don't filter them)
            for key, value in kwargs.items():
                engine_args.append(f"--{key.replace('_', '-')}={value}")

            # Add any remaining arguments
            engine_args.extend(remaining_args)

            # Try new engine first, fall back to helper
            template_engine = repo_root / "tools" / "repoman" / "template_engine.py"
            template_helper = repo_root / "tools" / "repoman" / "template_helper.py"

            if template_engine.exists():
                # Run template engine to generate playbook
                import subprocess
                python_cmd = get_python_command(repo_root)

                try:
                    # Run template_engine with stderr passthrough so user sees progress messages
                    result = subprocess.run([
                        python_cmd, str(template_engine)
                    ] + engine_args,
                    capture_output=False,  # Let stderr passthrough
                    stdout=subprocess.PIPE,  # But capture stdout (playback file path)
                    text=True, cwd=str(repo_root))

                    if result.returncode != 0:
                        return result.returncode

                    playback_file = result.stdout.strip()

                    # Check if this is a standalone project by reading the playback file
                    standalone_dir = None
                    try:
                        try:
                            import tomllib
                            # Python 3.11+ tomllib needs binary mode
                            with open(playback_file, 'rb') as f:
                                playback_data = tomllib.load(f)
                        except ImportError:
                            # Fallback to toml library which needs text mode
                            import toml
                            with open(playback_file, 'r') as f:
                                playback_data = toml.load(f)

                        if "_standalone_project" in playback_data:
                            standalone_dir = playback_data["_standalone_project"].get("output_directory")
                    except Exception:
                        pass  # If we can't read it, proceed normally

                    # Run template replay in the repo root (normal behavior)
                    # Note: Standalone projects with --output-dir need additional work
                    # to properly relocate files post-replay (future enhancement)
                    result = subprocess.run([
                        python_cmd, str(repo_root / "tools" / "repoman" / "repoman.py"),
                        "template", "replay", playback_file
                    ], cwd=str(repo_root))

                    # Post-process: Fix directory structure for applications
                    # The replay creates _build/apps/{name}.kit as a FILE
                    # We need to restructure it as _build/apps/{name}/{name}.kit
                    if result.returncode == 0:
                        _fix_application_structure(repo_root, playback_data)

                    return result.returncode

                except Exception as e:
                    print(f"Error running template engine: {e}", file=sys.stderr)
                    return 1

            elif template_helper.exists():
                # Fallback to old helper
                legacy_args = [template_name]
                if "name" in kwargs:
                    legacy_args.append(kwargs["name"])
                if "display_name" in kwargs:
                    legacy_args.append(kwargs["display_name"])
                if "version" in kwargs:
                    legacy_args.append(kwargs["version"])

                import subprocess
                python_cmd = get_python_command(repo_root)

                try:
                    result = subprocess.run([
                        python_cmd, str(template_helper)
                    ] + legacy_args,
                    capture_output=True, text=True, cwd=str(repo_root))

                    if result.returncode != 0:
                        print(result.stderr, file=sys.stderr)
                        return result.returncode

                    playback_file = result.stdout.strip()

                    # Run template replay with generated playbook file
                    result = subprocess.run([
                        python_cmd, str(repo_root / "tools" / "repoman" / "repoman.py"),
                        "template", "replay", playback_file
                    ], cwd=str(repo_root))

                    # Post-process: Fix directory structure for applications
                    if result.returncode == 0:
                        # Read playback data
                        try:
                            import tomllib
                            with open(playback_file, 'rb') as f:
                                playback_data = tomllib.load(f)
                        except ImportError:
                            import toml
                            with open(playback_file, 'r') as f:
                                playback_data = toml.load(f)

                        _fix_application_structure(repo_root, playback_data)

                    return result.returncode

                except Exception as e:
                    print(f"Error running template helper: {e}", file=sys.stderr)
                    return 1
            else:
                print("Error: Neither template_engine.py nor template_helper.py found", file=sys.stderr)
                return 1

        except ValueError as e:
            print(f"Error parsing arguments: {e}", file=sys.stderr)
            return 1

    elif subcommand == "docs":
        # Handle template docs command
        template_engine = repo_root / "tools" / "repoman" / "template_engine.py"
        if template_engine.exists():
            import subprocess
            python_cmd = get_python_command(repo_root)

            docs_args = ["docs"]
            if len(args) == 2:
                # No template specified, show all docs
                docs_args.append("--all")
            else:
                # Add remaining arguments
                docs_args.extend(args[2:])

            return subprocess.run([
                python_cmd, str(template_engine)
            ] + docs_args, cwd=str(repo_root)).returncode
        else:
            return call_repoman(args)

    elif subcommand == "list":
        # Handle template list command
        template_engine = repo_root / "tools" / "repoman" / "template_engine.py"
        if template_engine.exists():
            import subprocess
            python_cmd = get_python_command(repo_root)

            list_args = ["list"]
            list_args.extend(args[2:])  # Add any additional arguments

            return subprocess.run([
                python_cmd, str(template_engine)
            ] + list_args, cwd=str(repo_root)).returncode
        else:
            return call_repoman(args)

    else:
        # Delegate to repoman for other template commands
        return call_repoman(args)

def get_python_command(repo_root: Path) -> str:
    """Get the appropriate Python command for this repository."""
    packman_python = repo_root / "tools" / "packman" / "python.sh"
    packman_python_bat = repo_root / "tools" / "packman" / "python.bat"

    if os.name == "nt" and packman_python_bat.exists():
        return str(packman_python_bat)
    elif packman_python.exists():
        return str(packman_python)
    else:
        return "python3" if os.name != "nt" else "python"

def call_repoman(args: List[str]) -> int:
    """Delegate to repoman.py for standard commands."""
    repo_root = get_repo_root()
    repoman_py = repo_root / "tools" / "repoman" / "repoman.py"

    if not repoman_py.exists():
        print(f"Error: {repoman_py} not found", file=sys.stderr)
        return 1

    import subprocess
    python_cmd = get_python_command(repo_root)

    return subprocess.run([
        python_cmd, str(repoman_py)
    ] + args, cwd=str(repo_root)).returncode

def main() -> int:
    """Main entry point."""
    args = sys.argv[1:]

    if not args:
        return call_repoman(args)

    # Handle template commands with enhanced functionality
    if args[0] == "template":
        return handle_template_command(args)
    else:
        # Delegate all other commands to repoman
        return call_repoman(args)

if __name__ == "__main__":
    sys.exit(main())
