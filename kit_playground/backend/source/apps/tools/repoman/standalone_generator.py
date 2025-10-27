#!/usr/bin/env python3
"""
Standalone Project Generator for Kit App Template.

Converts template-generated projects into self-contained standalone projects
that can be built and run independently of the repository.
"""

import shutil
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StandaloneGenerator:
    """Generate standalone projects from templates."""

    def __init__(self, repo_root: Path):
        """
        Initialize generator.

        Args:
            repo_root: Path to kit-app-template repository root
        """
        self.repo_root = Path(repo_root).resolve()

    def generate_standalone(
        self,
        template_output_dir: Path,
        standalone_dir: Path,
        template_name: str,
        app_name: str,
        template_type: str = "application"
    ) -> Path:
        """
        Convert a template-generated project into a standalone project.

        Args:
            template_output_dir: Directory where template created the app
            standalone_dir: Target directory for standalone project
            template_name: Name of template used
            app_name: Application name
            template_type: Type of template (application, extension, microservice)

        Returns:
            Path to created standalone project

        Raises:
            FileNotFoundError: If source files don't exist
            FileExistsError: If standalone_dir already exists
        """
        template_output_dir = Path(template_output_dir).resolve()
        standalone_dir = Path(standalone_dir).resolve()

        logger.info(f"Generating standalone project: {standalone_dir}")
        logger.info(f"  Template: {template_name}")
        logger.info(f"  App name: {app_name}")
        logger.info(f"  Type: {template_type}")

        # Verify source exists
        if not template_output_dir.exists():
            raise FileNotFoundError(f"Template output not found: {template_output_dir}")

        # Create standalone directory
        if standalone_dir.exists():
            raise FileExistsError(f"Standalone directory already exists: {standalone_dir}")

        standalone_dir.mkdir(parents=True, exist_ok=False)

        try:
            # 1. Copy application/extension files
            self._copy_application(template_output_dir, standalone_dir, app_name, template_type)

            # 2. Copy build tools
            self._copy_build_tools(standalone_dir)

            # 3. Copy and modify configuration files
            self._copy_config_files(standalone_dir, app_name, template_type)

            # 4. Generate standalone-specific files
            self._generate_premake(standalone_dir, app_name, template_type)
            self._generate_readme(standalone_dir, template_name, app_name, template_type)

            logger.info(f"✓ Standalone project created: {standalone_dir}")
            return standalone_dir

        except Exception as e:
            # Cleanup on failure
            logger.error(f"Failed to generate standalone project: {e}")
            if standalone_dir.exists():
                shutil.rmtree(standalone_dir)
            raise

    def _copy_application(
        self,
        src_dir: Path,
        dest_dir: Path,
        app_name: str,
        template_type: str
    ):
        """Copy application source files to standalone project."""
        logger.info("Copying application files...")

        # Create source directory structure
        if template_type == "extension":
            dest_source = dest_dir / "source" / "extensions" / app_name
        else:  # application or microservice
            dest_source = dest_dir / "source" / "apps" / app_name

        dest_source.parent.mkdir(parents=True, exist_ok=True)

        # Copy the entire application directory
        shutil.copytree(src_dir, dest_source, dirs_exist_ok=True)

        logger.info(f"  ✓ Copied to: {dest_source.relative_to(dest_dir)}")

    def _copy_build_tools(self, dest_dir: Path):
        """Copy packman and repoman tools."""
        logger.info("Copying build tools...")

        tools_dest = dest_dir / "tools"
        tools_dest.mkdir(parents=True, exist_ok=True)

        # Copy packman (full directory)
        packman_src = self.repo_root / "tools" / "packman"
        packman_dest = tools_dest / "packman"
        if packman_src.exists():
            shutil.copytree(packman_src, packman_dest, dirs_exist_ok=True)
            logger.info(f"  ✓ Copied packman")

        # Copy repoman (core files only)
        repoman_src = self.repo_root / "tools" / "repoman"
        repoman_dest = tools_dest / "repoman"
        repoman_dest.mkdir(parents=True, exist_ok=True)

        # Essential repoman files
        repoman_files = [
            "repoman.py",
            "repo_dispatcher.py",
            "launch.py",
            "package.py",
            "template_api.py",
            "license_manager.py",
        ]

        for filename in repoman_files:
            src_file = repoman_src / filename
            if src_file.exists():
                shutil.copy2(src_file, repoman_dest / filename)

        logger.info(f"  ✓ Copied repoman ({len(repoman_files)} files)")

        # Copy other tool scripts if needed
        for script in ["package.sh", "package.bat", "validate_icons.py", "VERSION.md"]:
            src_file = self.repo_root / "tools" / script
            if src_file.exists():
                shutil.copy2(src_file, tools_dest / script)

    def _copy_config_files(
        self,
        dest_dir: Path,
        app_name: str,
        template_type: str
    ):
        """Copy and modify configuration files for standalone operation."""
        logger.info("Copying configuration files...")

        # Copy repo.sh and repo.bat (main scripts, not wrappers)
        for script in ["repo.sh", "repo.bat"]:
            src_file = self.repo_root / script
            dest_file = dest_dir / script
            if src_file.exists():
                shutil.copy2(src_file, dest_file)
                # Make executable on Unix
                if script.endswith(".sh"):
                    dest_file.chmod(0o755)

        logger.info(f"  ✓ Copied repo.sh and repo.bat")

        # Copy repo.toml (will need modifications)
        src_toml = self.repo_root / "repo.toml"
        dest_toml = dest_dir / "repo.toml"
        if src_toml.exists():
            shutil.copy2(src_toml, dest_toml)
            logger.info(f"  ✓ Copied repo.toml")

        # Copy repo_tools.toml if exists
        src_tools_toml = self.repo_root / "repo_tools.toml"
        dest_tools_toml = dest_dir / "repo_tools.toml"
        if src_tools_toml.exists():
            shutil.copy2(src_tools_toml, dest_tools_toml)

        # Copy requirements.txt if exists
        src_req = self.repo_root / "requirements.txt"
        dest_req = dest_dir / "requirements.txt"
        if src_req.exists():
            shutil.copy2(src_req, dest_req)
            logger.info(f"  ✓ Copied requirements.txt")

    def _generate_premake(
        self,
        dest_dir: Path,
        app_name: str,
        template_type: str
    ):
        """Generate standalone premake5.lua."""
        logger.info("Generating premake5.lua...")

        premake_file = dest_dir / "premake5.lua"

        # Determine source path based on template type
        if template_type == "extension":
            app_path = f"source/extensions/{app_name}"
        else:
            app_path = f"source/apps/{app_name}"

        premake_content = f'''-- Standalone premake5.lua for {app_name}
-- Generated by kit-app-template standalone generator

-- Configuration
BUILD_CONFIG = _OPTIONS["config"] or "release"
BUILD_DIR = "_build"

-- Root workspace
workspace "{app_name}"
    configurations {{ "debug", "release" }}
    platforms {{ "x86_64" }}

    location(BUILD_DIR)

    -- Architecture
    architecture "x86_64"

    -- Configuration-specific settings
    filter "configurations:debug"
        defines {{ "DEBUG" }}
        symbols "On"
        optimize "Off"

    filter "configurations:release"
        defines {{ "NDEBUG" }}
        symbols "Off"
        optimize "On"

    filter {{}}

-- Include application/extension build if present
local app_premake = "{app_path}/premake5.lua"
if os.isfile(app_premake) then
    include(app_premake)
end

-- Print build information
print("Building standalone project: {app_name}")
print("Configuration: " .. BUILD_CONFIG)
print("Build directory: " .. BUILD_DIR)
'''

        premake_file.write_text(premake_content)
        logger.info(f"  ✓ Generated premake5.lua")

    def _generate_readme(
        self,
        dest_dir: Path,
        template_name: str,
        app_name: str,
        template_type: str
    ):
        """Generate standalone README.md with usage instructions."""
        logger.info("Generating README.md...")

        readme_file = dest_dir / "README.md"

        readme_content = f'''# {app_name} - Standalone Project

This is a standalone Kit application generated from the `{template_name}` template.

## About This Project

- **Template**: {template_name}
- **Type**: {template_type}
- **Name**: {app_name}
- **Generated**: Standalone (self-contained)

## Project Structure

```
{dest_dir.name}/
├── repo.sh / repo.bat      # Build scripts
├── repo.toml               # Configuration
├── premake5.lua            # Build configuration
├── tools/                  # Build tools
│   ├── packman/            # Dependency manager
│   └── repoman/            # Build system
├── source/                 # Source code
│   └── {"extensions" if template_type == "extension" else "apps"}/{app_name}/
└── README.md               # This file
```

## Getting Started

### Prerequisites

- Python 3.7 or later
- Git (optional, for version control)
- Linux or Windows operating system

### Building

Build the project:

```bash
# Linux/macOS
./repo.sh build

# Windows
.\\repo.bat build
```

### Running

Launch the application:

```bash
# Linux/macOS
./repo.sh launch --name {app_name}.kit

# Windows
.\\repo.bat launch --name {app_name}.kit
```

## Available Commands

### Build Commands

```bash
./repo.sh build [--config <release|debug>]
```

Build the project. Default configuration is `release`.

### Launch Commands

```bash
./repo.sh launch --name {app_name}.kit [additional args]
```

Launch the built application.

### Package Commands

```bash
./repo.sh package
```

Create a distributable package of your application.

## Development Workflow

1. **Modify source code** in `source/{"extensions" if template_type == "extension" else "apps"}/{app_name}/`
2. **Rebuild**: `./repo.sh build`
3. **Test**: `./repo.sh launch --name {app_name}.kit`
4. **Package**: `./repo.sh package` (when ready to distribute)

## Directory Information

### Build Output

After building, you'll find:
- `_build/` - Build artifacts and compiled binaries
- `_build/linux-x86_64/release/` (or debug) - Platform-specific build output

### Configuration Files

- `repo.toml` - Main configuration file
- `premake5.lua` - Build system configuration
- `.project-meta.toml` - Project metadata (in app directory)

## Troubleshooting

### Build Fails

1. Ensure Python 3.7+ is installed: `python3 --version`
2. Check build output for specific errors
3. Try clean build: `./repo.sh build --clean`

### Launch Fails

1. Ensure project is built: `./repo.sh build`
2. Verify `.kit` file exists in build output
3. Check for error messages in console

### Missing Dependencies

Dependencies are managed by `packman` and downloaded automatically during first build.
If download fails:
1. Check internet connection
2. Check firewall/proxy settings
3. Review packman logs in `_build/`

## Distribution

This standalone project can be:
- ✅ Moved to any directory
- ✅ Shared with others (zip/tar the entire directory)
- ✅ Version controlled with Git
- ✅ Built independently without kit-app-template repository

### Sharing Your Project

To share this project:

```bash
# Create archive
tar -czf {app_name}.tar.gz {dest_dir.name}/

# Or zip
zip -r {app_name}.zip {dest_dir.name}/
```

Recipients can extract and build immediately:
```bash
tar -xzf {app_name}.tar.gz
cd {dest_dir.name}
./repo.sh build
```

## Learn More

### Kit App Template

This project was generated from [kit-app-template](https://github.com/NVIDIA-Omniverse/kit-app-template).

For more information about Kit development:
- [NVIDIA Omniverse Kit Documentation](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/index.html)
- [Kit App Template Docs](https://github.com/NVIDIA-Omniverse/kit-app-template/blob/main/README.md)

### Template Information

Original template: `{template_name}`

## License

See LICENSE file (if present) or refer to the Kit SDK license.

## Support

For issues related to:
- **This standalone project**: Check the original kit-app-template documentation
- **Kit SDK**: Visit NVIDIA Omniverse forums
- **Build system**: Review repoman and packman documentation in `tools/`

---

**Generated by**: kit-app-template standalone generator
**Template**: {template_name}
**Type**: {template_type}
**Self-contained**: Yes (no external dependencies on kit-app-template repository)
'''

        readme_file.write_text(readme_content)
        logger.info(f"  ✓ Generated README.md")


# CLI Helper Function
def create_standalone_project(
    repo_root: Path,
    template_output_dir: Path,
    output_dir: Optional[Path],
    template_name: str,
    app_name: str,
    template_type: str = "application"
) -> Path:
    """
    Create standalone project (convenience function for CLI).

    Args:
        repo_root: Repository root directory
        template_output_dir: Where template generated the app
        output_dir: Where to create standalone (or None for default)
        template_name: Template name
        app_name: Application name
        template_type: Template type

    Returns:
        Path to created standalone project
    """
    generator = StandaloneGenerator(repo_root)

    # Determine standalone directory
    if output_dir is None:
        # Default: create in current directory with app name
        standalone_dir = Path.cwd() / app_name
    else:
        standalone_dir = Path(output_dir)

    return generator.generate_standalone(
        template_output_dir=template_output_dir,
        standalone_dir=standalone_dir,
        template_name=template_name,
        app_name=app_name,
        template_type=template_type
    )


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 4:
        print("Usage: standalone_generator.py <repo_root> <template_output> <standalone_dir> <app_name>")
        sys.exit(1)

    repo_root = Path(sys.argv[1])
    template_output = Path(sys.argv[2])
    standalone_dir = Path(sys.argv[3])
    app_name = sys.argv[4] if len(sys.argv) > 4 else "my_app"

    logging.basicConfig(level=logging.INFO, format='%(message)s')

    try:
        result = create_standalone_project(
            repo_root=repo_root,
            template_output_dir=template_output,
            output_dir=standalone_dir,
            template_name="unknown",
            app_name=app_name
        )
        print(f"\n✓ Standalone project created: {result}")
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
