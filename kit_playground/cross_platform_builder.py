#!/usr/bin/env python3
"""
Native Electron app builder for Kit Playground.

This script builds the Electron app natively for Linux on any architecture
(x86_64, ARM64, etc). electron-builder automatically detects and builds for
the host architecture.
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


class NativeLinuxBuilder:
    """Handles native Linux Electron app building for any architecture."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.playground_dir = repo_root / "kit_playground"
        self.ui_dir = self.playground_dir / "ui"
        self.dist_dir = self.ui_dir / "dist"
        self.system = platform.system()
        self.arch = platform.machine()

    def check_prerequisites(self) -> bool:
        """Check if required tools are available."""
        has_node = shutil.which("node") is not None
        has_npm = shutil.which("npm") is not None
        has_python = (shutil.which("python3") is not None or
                     shutil.which("python") is not None)

        if not has_node or not has_npm:
            print("❌ Node.js and npm are required. Please install them first.")
            return False

        if not has_python:
            print("❌ Python is required. Please install it first.")
            return False

        return True

    def get_python_command(self) -> str:
        """Get the appropriate Python command for this system."""
        if self.system == "Windows":
            # Try py launcher first, then python
            if shutil.which("py"):
                return "py"
            elif shutil.which("python"):
                return "python"
        else:
            if shutil.which("python3"):
                return "python3"
            elif shutil.which("python"):
                return "python"

        raise RuntimeError("Python not found on system")

    def get_npm_command(self) -> str:
        """Get the appropriate npm command for this system."""
        if shutil.which("npm"):
            return "npm"
        raise RuntimeError("npm not found on system")

    def install_dependencies(self) -> bool:
        """Install Node.js and Python dependencies."""
        print("📦 Installing dependencies...")

        try:
            # Install npm dependencies
            npm_cmd = self.get_npm_command()
            subprocess.run([npm_cmd, "install"], cwd=self.ui_dir, check=True)

            # Install Python dependencies
            python_cmd = self.get_python_command()
            requirements_file = self.playground_dir / "backend" / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([
                    python_cmd, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)

            print("✅ Dependencies installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    def build_react_app(self) -> bool:
        """Build the React application."""
        print("🔨 Building React app...")

        try:
            npm_cmd = self.get_npm_command()
            subprocess.run([npm_cmd, "run", "build"], cwd=self.ui_dir, check=True)
            print("✅ React app built successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build React app: {e}")
            return False

    def build_electron(self) -> bool:
        """Build Electron app natively for Linux."""
        print(f"🔨 Building Electron app for Linux {self.arch}...")

        try:
            npm_cmd = self.get_npm_command()
            cmd = [npm_cmd, "run", "dist", "--", "--linux"]
            subprocess.run(cmd, cwd=self.ui_dir, check=True)
            print("✅ Electron app built successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build Electron app: {e}")
            return False

    def build(self) -> bool:
        """Build the Electron app for Linux."""
        print("=" * 50)
        print("Kit Playground Native Linux Builder")
        print("=" * 50)
        print(f"🖥️  System: {self.system} {self.arch}")
        print(f"📦 Node.js: {self.get_npm_command()}")
        print(f"🐍 Python: {self.get_python_command()}")
        print()

        # Check prerequisites
        if not self.check_prerequisites():
            return False

        # Install dependencies
        if not self.install_dependencies():
            return False

        # Build React app
        if not self.build_react_app():
            return False

        # Build Electron app
        return self.build_electron()

    def list_outputs(self) -> List[Path]:
        """List built output files."""
        if not self.dist_dir.exists():
            return []

        outputs = []
        for pattern in ["*.exe", "*.dmg", "*.AppImage", "*.deb", "*.rpm"]:
            outputs.extend(self.dist_dir.glob(pattern))

        return sorted(outputs)

    def print_summary(self) -> None:
        """Print build summary."""
        outputs = self.list_outputs()

        print()
        print("=" * 50)
        print("Build Summary")
        print("=" * 50)

        if outputs:
            print("📦 Built packages:")
            for output in outputs:
                size = output.stat().st_size / (1024 * 1024)  # MB
                print(f"  • {output.name} ({size:.1f} MB)")
                print(f"    Path: {output}")
        else:
            print("❌ No output packages found")

        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Native Linux Electron app builder for Kit Playground"
    )
    parser.add_argument(
        "--list-outputs", "-l",
        action="store_true",
        help="List built output files"
    )

    args = parser.parse_args()

    # Find repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    builder = NativeLinuxBuilder(repo_root)

    if args.list_outputs:
        outputs = builder.list_outputs()
        if outputs:
            print("Built packages:")
            for output in outputs:
                print(f"  {output}")
        else:
            print("No built packages found")
        return

    # Build the app
    success = builder.build()

    # Print summary
    builder.print_summary()

    if success:
        print("✅ Build completed successfully!")
        sys.exit(0)
    else:
        print("❌ Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
