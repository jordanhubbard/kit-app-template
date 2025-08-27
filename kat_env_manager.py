#!/usr/bin/env python3
"""
Kat Manager Environment Manager

Handles virtual environment creation, dependency management, and cross-platform
operations for the Kat Manager system. This provides the common logic used
by both Windows and Linux entrypoints.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class KatEnvManager:
    """Manages the Kat Manager virtual environment and operations."""
    
    def __init__(self, root_dir: Path = None):
        self.root_dir = root_dir or Path(__file__).parent
        self.venv_dir = self.root_dir / "_kat_venv"
        self.source_dir = self.venv_dir / "source"
        self.deployed_dir = self.venv_dir / "deployed"
        self.is_windows = platform.system() == "Windows"
        
        # Determine python executable paths
        if self.is_windows:
            self.python_exe = self.venv_dir / "Scripts" / "python.exe"
            self.pip_exe = self.venv_dir / "Scripts" / "pip.exe"
        else:
            self.python_exe = self.venv_dir / "bin" / "python"
            self.pip_exe = self.venv_dir / "bin" / "pip"
    
    def ensure_venv(self):
        """Create virtual environment if it doesn't exist."""
        if self.venv_dir.exists():
            return True
        
        print(f"🔧 Creating virtual environment: {self.venv_dir}")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_dir)
            ], check=True, capture_output=True)
            print(f"✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self, force_reinstall=False):
        """Install pip dependencies in the virtual environment."""
        requirements_file = self.root_dir / "requirements.txt"
        
        if not requirements_file.exists():
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        # Check if dependencies are already installed (unless forcing reinstall)
        if not force_reinstall:
            try:
                # Quick check - try importing the main dependencies
                result = subprocess.run([
                    str(self.python_exe), "-c", 
                    "import jinja2, yaml, jsonschema; print('ok')"
                ], capture_output=True, text=True)
                if result.returncode == 0 and "ok" in result.stdout:
                    return True  # Dependencies already installed, no output needed
            except:
                pass  # Fall through to installation
        
        print("📦 Installing dependencies...")
        try:
            # Upgrade pip first
            subprocess.run([
                str(self.pip_exe), "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([
                str(self.pip_exe), "install", "-r", str(requirements_file)
            ], check=True, capture_output=True)
            
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_environment(self):
        """Ensure virtual environment exists and dependencies are installed."""
        venv_created = not self.venv_dir.exists()
        
        if not self.ensure_venv():
            return False
        
        # Only force reinstall if we just created the venv
        if not self.install_dependencies(force_reinstall=venv_created):
            return False
        
        # Create source directory for generated templates
        self.source_dir.mkdir(exist_ok=True)
        
        # Create deployed directory for deployed applications  
        self.deployed_dir.mkdir(exist_ok=True)
        
        return True
    
    def run_kat_manager(self, args):
        """Run the kat-manager command in the virtual environment."""
        if not self.setup_environment():
            return 1

        kat_manager_script = self.root_dir / "kat-manager"

        # Build command to run in venv
        cmd = [str(self.python_exe), str(kat_manager_script)] + args

        # Set environment variables for the kat-manager script
        env = os.environ.copy()
        env['KAT_MANAGER_SOURCE_DIR'] = str(self.source_dir)
        env['KAT_MANAGER_ROOT_DIR'] = str(self.root_dir)
        
        try:
            result = subprocess.run(cmd, env=env)
            return result.returncode
        except Exception as e:
            print(f"❌ Error running kat-manager: {e}")
            return 1
    
    def clean(self):
        """Remove the virtual environment and all generated content."""
        if not self.venv_dir.exists():
            print("✅ No virtual environment to clean")
            return True
        
        print(f"🧹 Cleaning virtual environment: {self.venv_dir}")
        try:
            shutil.rmtree(self.venv_dir)
            print("✅ Virtual environment cleaned successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to clean virtual environment: {e}")
            return False
    
    def list_generated(self):
        """List all generated applications and extensions."""
        if not self.source_dir.exists():
            print("No generated templates found")
            return
        
        apps = []
        extensions = []
        
        apps_dir = self.source_dir / "apps"
        if apps_dir.exists():
            apps = [d.name for d in apps_dir.iterdir() if d.is_dir()]
        
        extensions_dir = self.source_dir / "extensions"
        if extensions_dir.exists():
            extensions = [d.name for d in extensions_dir.iterdir() if d.is_dir()]
        
        if apps:
            print("🎯 Generated Applications:")
            for app in apps:
                print(f"   • {app}")
        
        if extensions:
            print("🔧 Generated Extensions:")
            for ext in extensions:
                print(f"   • {ext}")
        
        if not apps and not extensions:
            print("No generated templates found")
    
    def deploy(self, source_name: str, target_path: str):
        """Deploy a generated application to a target location."""
        # Look for the app in both apps and extensions
        source_paths = [
            self.source_dir / "apps" / source_name,
            self.source_dir / "extensions" / source_name
        ]
        
        source_path = None
        for path in source_paths:
            if path.exists():
                source_path = path
                break
        
        if not source_path:
            print(f"❌ Generated template '{source_name}' not found")
            self.list_generated()
            return False
        
        target_path = Path(target_path).resolve()
        
        # If target is a directory, deploy into it
        if target_path.is_dir():
            target_path = target_path / source_name
        
        print(f"📤 Deploying {source_name}")
        print(f"   From: {source_path}")
        print(f"   To: {target_path}")
        
        try:
            # Create parent directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the entire directory
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
            
            # Also copy to deployed directory for tracking
            deployed_target = self.deployed_dir / source_name
            if deployed_target.exists():
                shutil.rmtree(deployed_target)
            shutil.copytree(source_path, deployed_target)
            
            print(f"✅ Successfully deployed to: {target_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to deploy: {e}")
            return False
    
    def status(self):
        """Show status of the Kat Manager environment."""
        print("🔍 Kat Manager Environment Status")
        print("=" * 40)
        
        print(f"Root Directory: {self.root_dir}")
        print(f"Virtual Environment: {self.venv_dir}")
        print(f"Environment Exists: {'✅ Yes' if self.venv_dir.exists() else '❌ No'}")
        
        if self.venv_dir.exists():
            print(f"Python Executable: {self.python_exe}")
            print(f"Source Directory: {self.source_dir}")
            print(f"Deployed Directory: {self.deployed_dir}")
            
            print("\n📊 Generated Templates:")
            self.list_generated()
            
            # Show deployed apps
            if self.deployed_dir.exists() and any(self.deployed_dir.iterdir()):
                print("\n📤 Deployed Templates:")
                for item in self.deployed_dir.iterdir():
                    if item.is_dir():
                        print(f"   • {item.name}")


def main():
    """Main entry point for the environment manager."""
    # Special handling for the run command to pass through all arguments
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # Pass all arguments after "run" to the kat-manager script
        manager = KatEnvManager()
        return manager.run_kat_manager(sys.argv[2:])
    
    parser = argparse.ArgumentParser(description="Kat Manager Environment Manager")
    parser.add_argument("command", choices=["setup", "clean", "status", "list", "deploy"])
    parser.add_argument("--source", help="Source template name for deploy command")
    parser.add_argument("--target", help="Target path for deploy command") 
    
    args = parser.parse_args()
    
    manager = KatEnvManager()
    
    if args.command == "setup":
        success = manager.setup_environment()
        return 0 if success else 1
    
    elif args.command == "clean":
        success = manager.clean()
        return 0 if success else 1
    
    elif args.command == "status":
        manager.status()
        return 0
    
    elif args.command == "list":
        manager.list_generated()
        return 0
    
    elif args.command == "deploy":
        if not args.source or not args.target:
            print("❌ Deploy command requires --source and --target arguments")
            return 1
        success = manager.deploy(args.source, args.target)
        return 0 if success else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
