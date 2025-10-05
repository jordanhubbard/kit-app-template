#!/usr/bin/env python3
"""
Cross-platform dependency checker and installer for Kit App Template.
Ensures required Python packages are available before running repo commands.
"""

import os
import sys
import subprocess
from pathlib import Path

def get_python_executable():
    """Get the current Python executable."""
    return sys.executable

def check_toml_available():
    """Check if toml library is available."""
    try:
        import tomllib
        return True, "tomllib (built-in)"
    except ImportError:
        pass

    try:
        import toml
        return True, "toml"
    except ImportError:
        pass

    try:
        import tomli
        return True, "tomli"
    except ImportError:
        pass

    return False, None

def install_toml_package(python_exe, quiet=True):
    """Install toml package using pip."""
    try:
        # Determine which package to install based on Python version
        version_info = sys.version_info
        if version_info >= (3, 11):
            # Python 3.11+ has tomllib built-in, but install tomli-w for writing
            packages = ["tomli-w"]
        else:
            # Python 3.10 and below need toml
            packages = ["toml"]

        for package in packages:
            cmd = [python_exe, "-m", "pip", "install"]
            if quiet:
                cmd.append("-q")
            cmd.append(package)

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stderr

        return True, None
    except Exception as e:
        return False, str(e)

def check_and_install_dependencies(verbose=False, force_install=False):
    """
    Check for required dependencies and install if missing.

    Args:
        verbose: If True, print detailed status messages
        force_install: If True, install even if dependency exists

    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    python_exe = get_python_executable()

    if verbose:
        print(f"Checking Python dependencies...")
        print(f"Using Python: {python_exe}")
        print(f"Python version: {sys.version}")
        print()

    # Check for toml library
    has_toml, toml_source = check_toml_available()

    if has_toml and not force_install:
        if verbose:
            print(f"✓ TOML library available ({toml_source})")
        return True

    if not has_toml:
        if verbose:
            print("✗ TOML library not found")
            print("  Installing required Python packages...")
        else:
            print("Installing required Python dependencies (first run only)...", file=sys.stderr)

        success, error = install_toml_package(python_exe, quiet=not verbose)

        if not success:
            print(f"Error: Failed to install Python dependencies", file=sys.stderr)
            if error:
                print(f"  {error}", file=sys.stderr)
            print(f"\nPlease install manually with:", file=sys.stderr)
            print(f"  {python_exe} -m pip install toml", file=sys.stderr)
            return False

        # Verify installation
        has_toml, toml_source = check_toml_available()
        if has_toml:
            if verbose:
                print(f"✓ Successfully installed TOML library ({toml_source})")
            else:
                print("✓ Dependencies installed successfully", file=sys.stderr)
            return True
        else:
            print("Error: Failed to verify TOML library installation", file=sys.stderr)
            return False

    return True

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check and install required Python dependencies"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed status messages"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstallation even if dependencies exist"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check, do not install"
    )

    args = parser.parse_args()

    if args.check_only:
        has_toml, toml_source = check_toml_available()
        if has_toml:
            if args.verbose:
                print(f"✓ TOML library available ({toml_source})")
            sys.exit(0)
        else:
            if args.verbose:
                print("✗ TOML library not found")
            sys.exit(1)

    success = check_and_install_dependencies(
        verbose=args.verbose,
        force_install=args.force
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
