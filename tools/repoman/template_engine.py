#!/usr/bin/env python3
"""
Enhanced template engine for Kit App Template system.
Provides data-driven, non-interactive template generation with
configuration inheritance, variable interpolation, and validation.
"""

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import copy

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
    try:
        import toml
        HAS_TOML = True
    except ImportError:
        HAS_TOML = False
        print("Warning: toml library not available. Limited functionality.", file=sys.stderr)

class TemplateConfigManager:
    """Manages template configuration loading, merging, and validation."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.templates_dir = self.repo_root / "templates"
        self.config_dir = self.templates_dir / "config"
        self.user_config_paths = [
            Path.home() / ".omni" / "kit-app-template" / "user.toml",
            Path.home() / ".config" / "omni" / "kit-app-template.toml",
            self.repo_root / "user-config.toml"
        ]

    def load_config_file(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load a TOML configuration file."""
        path = Path(path)
        if not path.exists():
            return {}

        try:
            if HAS_TOMLLIB:
                with open(path, 'rb') as f:
                    return tomllib.load(f)
            elif HAS_TOML:
                with open(path, 'r') as f:
                    return toml.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading config file {path}: {e}", file=sys.stderr)
            return {}

    def find_user_config(self) -> Optional[Path]:
        """Find the first available user configuration file."""
        for path in self.user_config_paths:
            if path.exists():
                return path
        return None

    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge multiple configuration dictionaries."""
        result = {}
        for config in configs:
            self._deep_merge(result, config)
        return result

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Recursively merge update dict into base dict."""
        for key, value in update.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    self._deep_merge(base[key], value)
                else:
                    base[key] = value
            else:
                base[key] = copy.deepcopy(value)
        return base

    def resolve_includes(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve 'includes' directives in configuration."""
        if 'includes' not in config:
            return config

        includes = config.pop('includes')
        if isinstance(includes, str):
            includes = [includes]

        base_configs = []
        for include in includes:
            include_path = self.config_dir / f"{include}.toml"
            if include_path.exists():
                included = self.load_config_file(include_path)
                included = self.resolve_includes(included)  # Recursive resolution
                base_configs.append(included)

        # Merge included configs first, then overlay current config
        result = self.merge_configs(*base_configs)
        result = self.merge_configs(result, config)
        return result

    def interpolate_variables(self, config: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Interpolate variables in configuration values."""
        if context is None:
            context = config.copy()
            context['env'] = dict(os.environ)

        def interpolate_value(value: Any) -> Any:
            if isinstance(value, str):
                # Find all ${var} patterns
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, value)

                for match in matches:
                    # Handle nested paths like company.name
                    parts = match.split('.')
                    replacement = context
                    for part in parts:
                        if isinstance(replacement, dict) and part in replacement:
                            replacement = replacement[part]
                        else:
                            replacement = f"${{{match}}}"  # Keep original if not found
                            break

                    if not isinstance(replacement, dict):
                        value = value.replace(f"${{{match}}}", str(replacement))

                return value
            elif isinstance(value, dict):
                return {k: interpolate_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [interpolate_value(v) for v in value]
            return value

        return interpolate_value(config)


class TemplateEngine:
    """Enhanced template engine for generating Kit applications and extensions."""

    # Template metadata from templates.toml
    TEMPLATES = {
        "kit_base_editor": {
            "class": "ApplicationTemplate",
            "name": "Kit Base Editor",
            "extensions": []
        },
        "omni_usd_composer": {
            "class": "ApplicationTemplate",
            "name": "USD Composer",
            "extensions": ["omni_usd_composer_setup"]
        },
        "omni_usd_explorer": {
            "class": "ApplicationTemplate",
            "name": "USD Explorer",
            "extensions": ["omni_usd_explorer_setup"]
        },
        "omni_usd_viewer": {
            "class": "ApplicationTemplate",
            "name": "USD Viewer",
            "extensions": ["omni_usd_viewer_messaging", "omni_usd_viewer_setup"]
        },
        "kit_service": {
            "class": "ApplicationTemplate",
            "name": "Kit Service",
            "extensions": ["kit_service_setup"]
        },
        "basic_python_extension": {
            "class": "ExtensionTemplate",
            "name": "Basic Python Extension"
        },
        "basic_python_ui_extension": {
            "class": "ExtensionTemplate",
            "name": "Python UI Extension"
        },
        "basic_cpp_extension": {
            "class": "ExtensionTemplate",
            "name": "Basic C++ Extension"
        },
        "basic_python_binding": {
            "class": "ExtensionTemplate",
            "name": "Basic C++ w/ Python Binding Extension"
        }
    }

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.config_manager = TemplateConfigManager(repo_root)

    def generate_template(self,
                         template_name: str,
                         config_file: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Generate template configuration with proper variable substitution.

        Args:
            template_name: Name of the template to generate
            config_file: Optional path to configuration file
            **kwargs: Override parameters (app_name, display_name, version, etc.)

        Returns:
            Dictionary containing the template playback configuration
        """
        if template_name not in self.TEMPLATES:
            raise ValueError(f"Unknown template '{template_name}'. Available: {list(self.TEMPLATES.keys())}")

        template_info = self.TEMPLATES[template_name]

        # Load and merge configurations
        config = self._build_configuration(template_name, config_file, kwargs)

        # Generate playback content
        playback = self._generate_playback(template_name, template_info, config)

        # Validate the generated configuration
        if not self._validate_playback(playback):
            raise ValueError("Generated playback configuration is invalid")

        return playback

    def _build_configuration(self, template_name: str, config_file: Optional[str], overrides: Dict) -> Dict[str, Any]:
        """Build the final configuration by merging all sources."""
        configs = []

        # 1. Load default template configuration
        default_config = self._get_default_config(template_name)
        configs.append(default_config)

        # 2. Load user configuration if exists
        user_config_path = self.config_manager.find_user_config()
        if user_config_path:
            user_config = self.config_manager.load_config_file(user_config_path)
            configs.append(user_config)

        # 3. Load specified configuration file
        if config_file:
            file_config = self.config_manager.load_config_file(config_file)
            file_config = self.config_manager.resolve_includes(file_config)
            configs.append(file_config)

        # 4. Apply command-line overrides
        if overrides:
            override_config = self._parse_overrides(template_name, overrides)
            configs.append(override_config)

        # Merge all configurations
        final_config = self.config_manager.merge_configs(*configs)

        # Interpolate variables
        final_config = self.config_manager.interpolate_variables(final_config)

        return final_config

    def _get_default_config(self, template_name: str) -> Dict[str, Any]:
        """Get default configuration for a template."""
        template_info = self.TEMPLATES[template_name]
        is_app = template_info["class"] == "ApplicationTemplate"

        # Generate sensible defaults
        clean_name = template_name.replace('_', '')

        return {
            "application" if is_app else "extension": {
                "name": f"my_company.my_{clean_name}",
                "display_name": f"My {template_info['name']}",
                "version": "0.1.0"
            }
        }

    def _parse_overrides(self, template_name: str, overrides: Dict) -> Dict[str, Any]:
        """Parse command-line override arguments into configuration."""
        config = {}

        # Check template type to determine correct mapping
        template_info = self.TEMPLATES.get(template_name, {})
        is_extension = template_info.get('class') == 'ExtensionTemplate'

        # Map common override keys to configuration structure
        if is_extension:
            mappings = {
                'app_name': 'extension.name',
                'name': 'extension.name',
                'display_name': 'extension.display_name',
                'version': 'extension.version',
                'ext_name': 'extension.name',
                'extension_name': 'extension.name',
                'extension_display_name': 'extension.display_name'
            }
        else:
            mappings = {
                'app_name': 'application.name',
                'name': 'application.name',
                'display_name': 'application.display_name',
                'version': 'application.version',
                'ext_name': 'extension.name',
                'extension_name': 'extension.name',
                'extension_display_name': 'extension.display_name'
            }

        for key, value in overrides.items():
            if value is None:
                continue

            # Use mapping if available, otherwise use key directly
            path = mappings.get(key, key)

            # Build nested dictionary from dot-separated path
            parts = path.split('.')
            current = config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

        return config

    def _generate_playback(self, template_name: str, template_info: Dict, config: Dict) -> Dict[str, Any]:
        """Generate the playback configuration for template replay."""
        is_app = template_info["class"] == "ApplicationTemplate"

        # Extract relevant configuration
        if is_app:
            app_config = config.get('application', {})
            app_name = app_config.get('name', f"my_company.my_{template_name}")
            display_name = app_config.get('display_name', f"My {template_info['name']}")
            version = app_config.get('version', '0.1.0')
        else:
            ext_config = config.get('extension', {})
            app_name = ext_config.get('name', f"my_company.my_{template_name}")
            display_name = ext_config.get('display_name', f"My {template_info['name']}")
            version = ext_config.get('version', '0.1.0')

        # Build playback content
        playback = {
            template_name: {
                f"{'application' if is_app else 'extension'}_name": app_name,
                f"{'application' if is_app else 'extension'}_display_name": display_name,
                "version": version
            }
        }

        # Add application-specific fields
        if is_app:
            playback[template_name]["add_layers"] = config.get('add_layers', 'No')

            # Add extension configurations for templates that have them
            if 'extensions' in template_info and template_info['extensions']:
                ext_configs = {}

                for ext_template in template_info['extensions']:
                    # Check if there's custom config for this extension
                    ext_config_key = ext_template.replace('omni_', '').replace('kit_', '')
                    custom_ext = config.get('extensions', {}).get(ext_config_key, {})

                    # Generate extension configuration
                    ext_suffix = ext_template.split('_')[-1]
                    ext_configs[ext_template] = {
                        "extension_name": custom_ext.get('name', f"{app_name}_{ext_suffix}"),
                        "extension_display_name": custom_ext.get('display_name', f"{display_name} {ext_suffix.title()}"),
                        "version": custom_ext.get('version', version)
                    }

                if ext_configs:
                    playback[template_name]["extensions"] = ext_configs

        return playback

    def _validate_playback(self, playback: Dict[str, Any]) -> bool:
        """Validate the generated playback configuration."""
        # Check for required fields
        if not playback or len(playback) != 1:
            return False

        template_name = list(playback.keys())[0]
        template_config = playback[template_name]

        # Check version format (must be semver compliant)
        version = template_config.get('version', '')
        if not re.match(r'^\d+\.\d+\.\d+(-[\w\.]+)?(\+[\w\.]+)?$', version):
            print(f"Invalid version format: {version}. Must be semver compliant (e.g., 1.0.0)", file=sys.stderr)
            return False

        # Check required fields based on template type
        if 'application_name' in template_config:
            required = ['application_name', 'application_display_name', 'version']
        else:
            required = ['extension_name', 'extension_display_name', 'version']

        for field in required:
            if field not in template_config:
                print(f"Missing required field: {field}", file=sys.stderr)
                return False
            if not template_config[field] or template_config[field] == "":
                print(f"Empty value for required field: {field}", file=sys.stderr)
                return False

        return True

    def save_playback_file(self, playback: Dict[str, Any]) -> str:
        """Save playback configuration to a temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            if HAS_TOMLI_W:
                tomli_w.dump(playback, f)
            elif HAS_TOML:
                toml.dump(playback, f)
            else:
                # Manual TOML writing
                self._write_toml_manual(f, playback)

            return f.name

    def _write_toml_manual(self, file, data: Dict[str, Any], prefix: str = ""):
        """Manually write TOML format when library is not available."""
        for key, value in data.items():
            if isinstance(value, dict):
                section = f"{prefix}.{key}" if prefix else key
                file.write(f"\n[{section}]\n")
                self._write_toml_manual(file, value, section)
            else:
                if isinstance(value, str):
                    file.write(f'{key} = "{value}"\n')
                else:
                    file.write(f'{key} = {value}\n')


def main():
    """Main entry point for template engine CLI."""
    if len(sys.argv) < 2:
        print("Usage: template_engine.py <template_name> [options]")
        print("Options:")
        print("  --config=<file>       Configuration file to use")
        print("  --name=<name>         Application/extension name")
        print("  --display-name=<name> Display name")
        print("  --version=<version>   Version (semver format)")
        print(f"\nAvailable templates: {list(TemplateEngine.TEMPLATES.keys())}")
        sys.exit(1)

    template_name = sys.argv[1]

    # Parse arguments
    kwargs = {}
    config_file = None

    for arg in sys.argv[2:]:
        if arg.startswith('--config='):
            config_file = arg.split('=', 1)[1]
        elif arg.startswith('--'):
            if '=' in arg:
                key, value = arg[2:].split('=', 1)
                kwargs[key.replace('-', '_')] = value

    # Backward compatibility with positional arguments
    if len(sys.argv) > 2 and not sys.argv[2].startswith('--'):
        kwargs['app_name'] = sys.argv[2]
    if len(sys.argv) > 3 and not sys.argv[3].startswith('--'):
        kwargs['display_name'] = sys.argv[3]
    if len(sys.argv) > 4 and not sys.argv[4].startswith('--'):
        kwargs['version'] = sys.argv[4]

    # Initialize engine
    repo_root = os.path.join(os.path.dirname(os.path.normpath(__file__)), "../..")
    engine = TemplateEngine(repo_root)

    try:
        # Generate template
        playback = engine.generate_template(template_name, config_file, **kwargs)

        # Save to file
        playback_file = engine.save_playback_file(playback)

        # Print file path for repo.sh to use
        print(playback_file)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()