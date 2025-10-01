#!/usr/bin/env python3
"""
Cross-platform Electron app builder for Kit Playground.

This script handles building the Electron app for Windows on Linux containers
or detects Windows for bare-metal builds, ensuring OS-agnostic functionality.
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class CrossPlatformBuilder:
    """Handles cross-platform Electron app building."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.playground_dir = repo_root / "kit_playground"
        self.ui_dir = self.playground_dir / "ui"
        self.dist_dir = self.playground_dir / "dist"
        self.system = platform.system()

    def detect_build_environment(self) -> Dict[str, bool]:
        """Detect available build environments and tools."""
        env = {
            "is_windows": self.system == "Windows",
            "is_linux": self.system == "Linux",
            "is_macos": self.system == "Darwin",
            "has_docker": shutil.which("docker") is not None,
            "has_wine": shutil.which("wine") is not None,
            "has_node": shutil.which("node") is not None,
            "has_npm": shutil.which("npm") is not None,
            "has_python": (shutil.which("python3") is not None or
                          shutil.which("python") is not None),
        }

        # Check for Wine in Docker if on Linux
        if env["is_linux"] and env["has_docker"]:
            try:
                result = subprocess.run([
                    "docker", "images", "electronuserland/builder:wine",
                    "--format", "{{.Repository}}:{{.Tag}}"
                ], capture_output=True, text=True, timeout=10, check=False)
                env["has_wine_docker"] = (
                    "electronuserland/builder:wine" in result.stdout
                )
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                env["has_wine_docker"] = False
        else:
            env["has_wine_docker"] = False

        return env

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

    def build_electron_native(self, target_platform: str = None) -> bool:
        """Build Electron app natively on the current platform."""
        print(f"🔨 Building Electron app for {target_platform or 'current platform'}...")

        try:
            npm_cmd = self.get_npm_command()

            if target_platform:
                # Cross-platform build
                if target_platform == "windows":
                    cmd = [npm_cmd, "run", "dist", "--", "--win"]
                elif target_platform == "linux":
                    cmd = [npm_cmd, "run", "dist", "--", "--linux"]
                elif target_platform == "macos":
                    cmd = [npm_cmd, "run", "dist", "--", "--mac"]
                else:
                    cmd = [npm_cmd, "run", "dist"]
            else:
                # Build for current platform
                cmd = [npm_cmd, "run", "dist"]

            subprocess.run(cmd, cwd=self.ui_dir, check=True)
            print("✅ Electron app built successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build Electron app: {e}")
            return False

    def build_electron_docker(self, target_platform: str = "windows") -> bool:
        """Build Electron app using Docker with Wine for Windows targets."""
        print(f"🐳 Building Electron app for {target_platform} using Docker...")

        try:
            # Ensure Docker image is available
            subprocess.run([
                "docker", "pull", "electronuserland/builder:wine"
            ], check=True)

            # Create dist directory if it doesn't exist
            self.dist_dir.mkdir(exist_ok=True)

            # Build command for Docker
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{self.ui_dir}:/project",
                "-v", f"{self.dist_dir}:/project/dist",
                "electronuserland/builder:wine"
            ]

            if target_platform == "windows":
                docker_cmd.extend(["npm", "run", "dist", "--", "--win"])
            elif target_platform == "linux":
                docker_cmd.extend(["npm", "run", "dist", "--", "--linux"])
            elif target_platform == "all":
                docker_cmd.extend(["npm", "run", "dist:all"])
            else:
                docker_cmd.extend(["npm", "run", "dist"])

            subprocess.run(docker_cmd, check=True)
            print("✅ Electron app built successfully using Docker")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build Electron app using Docker: {e}")
            return False

    def get_build_strategy(self, target_platform: str = None) -> Tuple[str, str]:
        """Determine the best build strategy for the target platform."""
        env = self.detect_build_environment()

        if not target_platform:
            target_platform = {
                "Windows": "windows",
                "Linux": "linux",
                "Darwin": "macos"
            }.get(self.system, "linux")

        # If building for current platform, use native build
        current_platform = {
            "Windows": "windows",
            "Linux": "linux",
            "Darwin": "macos"
        }.get(self.system)

        if target_platform == current_platform:
            return "native", f"Building natively on {self.system}"

        # Cross-platform build strategies
        if target_platform == "windows":
            if env["is_linux"] and env["has_wine_docker"]:
                return "docker", "Using Docker with Wine for Windows build on Linux"
            elif env["is_linux"] and env["has_wine"]:
                return "native", "Using Wine for Windows build on Linux"
            elif env["is_windows"]:
                return "native", "Building natively on Windows"
            else:
                return "unsupported", f"Cannot build Windows app on {self.system} without Wine/Docker"

        elif target_platform == "linux":
            if env["is_linux"]:
                return "native", "Building natively on Linux"
            elif env["has_docker"]:
                return "docker", "Using Docker for Linux build"
            else:
                return "unsupported", f"Cannot build Linux app on {self.system} without Docker"

        elif target_platform == "macos":
            if env["is_macos"]:
                return "native", "Building natively on macOS"
            else:
                return "unsupported", "macOS builds require macOS (code signing limitations)"

        return "unsupported", f"Unsupported target platform: {target_platform}"

    def build(self, target_platform: str = None, force_docker: bool = False) -> bool:
        """Build the Electron app for the specified platform."""
        print("=" * 50)
        print("Kit Playground Cross-Platform Builder")
        print("=" * 50)

        # Detect environment
        env = self.detect_build_environment()
        print(f"🖥️  System: {self.system}")
        print(f"🐳 Docker: {'✅' if env['has_docker'] else '❌'}")
        print(f"🍷 Wine: {'✅' if env['has_wine'] or env.get('has_wine_docker') else '❌'}")
        print(f"📦 Node.js: {'✅' if env['has_node'] else '❌'}")
        print(f"🐍 Python: {'✅' if env['has_python'] else '❌'}")
        print()

        # Check prerequisites
        if not env["has_node"] or not env["has_npm"]:
            print("❌ Node.js and npm are required. Please install them first.")
            return False

        if not env["has_python"]:
            print("❌ Python is required. Please install it first.")
            return False

        # Install dependencies
        if not self.install_dependencies():
            return False

        # Build React app
        if not self.build_react_app():
            return False

        # Determine build strategy
        strategy, reason = self.get_build_strategy(target_platform)
        print(f"🎯 Build strategy: {strategy}")
        print(f"📝 Reason: {reason}")
        print()

        if strategy == "unsupported":
            print(f"❌ {reason}")
            return False

        # Execute build
        if force_docker or strategy == "docker":
            return self.build_electron_docker(target_platform)
        else:
            return self.build_electron_native(target_platform)

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
        description="Cross-platform Electron app builder for Kit Playground"
    )
    parser.add_argument(
        "--target", "-t",
        choices=["windows", "linux", "macos", "all"],
        help="Target platform to build for (default: current platform)"
    )
    parser.add_argument(
        "--docker", "-d",
        action="store_true",
        help="Force use of Docker for building"
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

    builder = CrossPlatformBuilder(repo_root)

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
    success = builder.build(args.target, args.docker)

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
