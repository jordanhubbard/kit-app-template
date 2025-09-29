#!/usr/bin/env python3
"""
OS-independent repo command dispatcher.
Handles enhanced template functionality and delegates other commands to repoman.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any

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
                    result = subprocess.run([
                        python_cmd, str(template_engine)
                    ] + engine_args,
                    capture_output=True, text=True, cwd=str(repo_root))

                    if result.returncode != 0:
                        print(result.stderr, file=sys.stderr)
                        return result.returncode

                    playback_file = result.stdout.strip()

                    # Run template replay with generated playbook file
                    return subprocess.run([
                        python_cmd, str(repo_root / "tools" / "repoman" / "repoman.py"),
                        "template", "replay", playback_file
                    ], cwd=str(repo_root)).returncode

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
                    return subprocess.run([
                        python_cmd, str(repo_root / "tools" / "repoman" / "repoman.py"),
                        "template", "replay", playback_file
                    ], cwd=str(repo_root)).returncode

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