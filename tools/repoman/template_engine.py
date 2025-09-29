#!/usr/bin/env python3
"""
Enhanced template engine for Kit App Template system.
Provides data-driven, non-interactive template generation with
configuration inheritance, variable interpolation, and validation.
"""

import json
import os
import re
import shutil
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


class TemplateDiscovery:
    """Discovers and loads templates from the new descriptor system."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.templates_dir = self.repo_root / "templates"
        self.registry_file = self.templates_dir / "template_registry.toml"
        self._templates_cache = None
        self._registry_cache = None

    def load_registry(self) -> Dict[str, Any]:
        """Load the template registry configuration."""
        if self._registry_cache is None:
            if self.registry_file.exists():
                config_manager = TemplateConfigManager(str(self.repo_root))
                self._registry_cache = config_manager.load_config_file(self.registry_file)
            else:
                self._registry_cache = {}
        return self._registry_cache

    def discover_templates(self) -> Dict[str, Dict[str, Any]]:
        """Discover all templates using the registry configuration."""
        if self._templates_cache is not None:
            return self._templates_cache

        registry = self.load_registry()
        templates = {}

        discovery_paths = registry.get('registry', {}).get('discovery', {}).get('paths', [])
        if not discovery_paths:
            # Fallback to hardcoded paths if registry not available
            discovery_paths = [
                "applications/*/template.toml",
                "extensions/*/template.toml",
                "extensions/*/*/template.toml",
                "microservices/*/template.toml",
                "components/*/template.toml",
                "components/*/*/template.toml"
            ]

        config_manager = TemplateConfigManager(str(self.repo_root))

        for pattern in discovery_paths:
            template_files = self.templates_dir.glob(pattern)
            for template_file in template_files:
                if template_file.is_file():
                    template_config = config_manager.load_config_file(template_file)
                    if 'metadata' in template_config:
                        template_name = template_config['metadata']['name']
                        template_config['_template_file'] = str(template_file)
                        template_config['_template_dir'] = str(template_file.parent)
                        templates[template_name] = template_config

        self._templates_cache = templates
        return templates

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name."""
        templates = self.discover_templates()
        return templates.get(name)

    def get_templates_by_type(self, template_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all templates of a specific type."""
        templates = self.discover_templates()
        return {name: config for name, config in templates.items()
                if config.get('metadata', {}).get('type') == template_type}

    def get_templates_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all templates of a specific category."""
        templates = self.discover_templates()
        return {name: config for name, config in templates.items()
                if config.get('metadata', {}).get('category') == category}


class TemplateEngine:
    """Enhanced template engine for generating Kit applications and extensions."""

    def list_templates(self, template_type: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List available templates, optionally filtered by type or category."""
        if template_type:
            return self.template_discovery.get_templates_by_type(template_type)
        elif category:
            return self.template_discovery.get_templates_by_category(category)
        else:
            return self.template_discovery.discover_templates()

    def get_template_documentation(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get documentation for a specific template."""
        template_config = self.template_discovery.get_template(template_name)
        if not template_config:
            return None

        return {
            'metadata': template_config.get('metadata', {}),
            'documentation': template_config.get('documentation', {}),
            'variables': template_config.get('variables', {}),
            'dependencies': template_config.get('dependencies', {}),
            'deployment': template_config.get('deployment', {}),
            'build': template_config.get('build', {})
        }

    def format_template_docs(self, template_name: str) -> Optional[str]:
        """Format template documentation as readable text."""
        docs = self.get_template_documentation(template_name)
        if not docs:
            return None

        metadata = docs['metadata']
        documentation = docs['documentation']
        variables = docs['variables']

        output = []
        output.append(f"# {metadata.get('display_name', template_name)}")
        output.append(f"Type: {metadata.get('type', 'unknown').title()}")
        if metadata.get('category'):
            output.append(f"Category: {metadata.get('category').title()}")
        output.append(f"Version: {metadata.get('version', 'unknown')}")
        output.append("")

        if documentation.get('overview'):
            output.append("## Overview")
            output.append(documentation['overview'].strip())
            output.append("")

        if documentation.get('use_cases'):
            output.append("## Use Cases")
            for use_case in documentation['use_cases']:
                output.append(f"- {use_case}")
            output.append("")

        if documentation.get('key_features'):
            output.append("## Key Features")
            for feature in documentation['key_features']:
                output.append(f"- {feature}")
            output.append("")

        if documentation.get('getting_started'):
            output.append("## Getting Started")
            output.append(documentation['getting_started'].strip())
            output.append("")

        if variables:
            output.append("## Default Variables")
            for key, value in variables.items():
                output.append(f"- {key}: {value}")
            output.append("")

        return "\n".join(output)

    def print_all_templates_docs(self) -> None:
        """Print documentation for all templates."""
        templates = self.template_discovery.discover_templates()

        # Group by type
        by_type = {}
        for name, config in templates.items():
            template_type = config.get('metadata', {}).get('type', 'unknown')
            if template_type not in by_type:
                by_type[template_type] = []
            by_type[template_type].append(name)

        for template_type in sorted(by_type.keys()):
            print(f"\n{'='*60}")
            print(f"{template_type.upper()} TEMPLATES")
            print(f"{'='*60}")

            for template_name in sorted(by_type[template_type]):
                docs = self.format_template_docs(template_name)
                if docs:
                    print(docs)
                    print("-" * 40)

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.config_manager = TemplateConfigManager(repo_root)
        self.template_discovery = TemplateDiscovery(repo_root)

    def generate_template(self,
                         template_name: str,
                         config_file: Optional[str] = None,
                         output_dir: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Generate template configuration with proper variable substitution.

        Args:
            template_name: Name of the template to generate
            config_file: Optional path to configuration file
            output_dir: Optional output directory for standalone projects
            **kwargs: Override parameters (app_name, display_name, version, etc.)

        Returns:
            Dictionary containing the template playbook configuration
        """

        # Handle output directory for standalone projects
        if output_dir:
            return self._generate_standalone_project(template_name, config_file, output_dir, **kwargs)
        template_config = self.template_discovery.get_template(template_name)
        if template_config is None:
            available = list(self.template_discovery.discover_templates().keys())
            raise ValueError(f"Unknown template '{template_name}'. Available: {available}")

        # Template configuration loaded successfully

        # Load and merge configurations
        config = self._build_configuration(template_name, config_file, kwargs)

        # Resolve template dependencies and composition
        resolved_config = self._resolve_template_composition(template_config, config)

        # Generate playback content
        playback = self._generate_playback(template_name, template_config, resolved_config)

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
        template_config = self.template_discovery.get_template(template_name)
        if not template_config:
            return {}

        template_type = template_config.get('metadata', {}).get('type', 'extension')
        template_class = template_config.get('template', {}).get('class', 'ExtensionTemplate')
        variables = template_config.get('variables', {})

        # Use template's default variables or generate sensible defaults
        if variables:
            return {template_type: variables}

        # Fallback to generated defaults
        clean_name = template_name.replace('_', '')
        is_app = template_class == "ApplicationTemplate"

        return {
            "application" if is_app else "extension": {
                "name": f"my_company.my_{clean_name}",
                "display_name": f"My {template_config.get('metadata', {}).get('display_name', clean_name)}",
                "version": "0.1.0"
            }
        }

    def _parse_overrides(self, template_name: str, overrides: Dict) -> Dict[str, Any]:
        """Parse command-line override arguments into configuration."""
        config = {}

        # Check template type to determine correct mapping
        template_config = self.template_discovery.get_template(template_name)
        template_class = template_config.get('template', {}).get('class') if template_config else 'ExtensionTemplate'
        is_extension = template_class == 'ExtensionTemplate'

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

    def _generate_playback(self, template_name: str, template_config: Dict, config: Dict) -> Dict[str, Any]:
        """Generate the playback configuration for template replay."""
        # Determine template type from new structure
        template_class = template_config.get('template', {}).get('class', 'ExtensionTemplate')
        template_type = template_config.get('metadata', {}).get('type', 'extension')
        is_app = template_class == "ApplicationTemplate" or template_type in ['application', 'microservice']

        # Extract relevant configuration
        if is_app:
            app_config = config.get('application', {})
            app_name = app_config.get('name', f"my_company.my_{template_name}")
            display_name = app_config.get('display_name', f"My {template_config.get('metadata', {}).get('display_name', template_name)}")
            version = app_config.get('version', '0.1.0')
        else:
            ext_config = config.get('extension', {})
            app_name = ext_config.get('name', f"my_company.my_{template_name}")
            display_name = ext_config.get('display_name', f"My {template_config.get('metadata', {}).get('display_name', template_name)}")
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
            if 'extensions' in template_config and template_config['extensions']:
                ext_configs = {}
                extensions = template_config['extensions']

                # Handle both legacy TOML format (list) and new format (dict)
                if isinstance(extensions, list):
                    # Legacy format: array of tables
                    for ext_item in extensions:
                        ext_template = ext_item.get('template')
                        if ext_template:
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
                elif isinstance(extensions, dict):
                    # New format: dictionary
                    for ext_key, ext_config in extensions.items():
                        ext_template = ext_config.get('template', ext_key)
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

    def _resolve_template_composition(self, template_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve template composition, inheritance, and dependencies."""
        resolved = copy.deepcopy(user_config)

        # Handle template inheritance via 'extends'
        if 'extends' in template_config.get('template', {}):
            parent_template_name = template_config['template']['extends']
            parent_config = self.template_discovery.get_template(parent_template_name)
            if parent_config:
                # Recursively resolve parent composition
                parent_resolved = self._resolve_template_composition(parent_config, user_config)
                # Merge parent configuration with current
                resolved = self.config_manager.merge_configs(parent_resolved, resolved)

        # Handle required extensions
        if 'requires_extensions' in template_config.get('template', {}):
            extensions_config = self._resolve_extension_dependencies(
                template_config['template']['requires_extensions'], user_config
            )
            resolved = self.config_manager.merge_configs(resolved, extensions_config)

        # Handle extensions defined in template
        if 'extensions' in template_config:
            for ext_key, ext_config in template_config['extensions'].items():
                if isinstance(ext_config, dict) and 'template' in ext_config:
                    ext_template_name = ext_config['template']
                    ext_template_config = self.template_discovery.get_template(ext_template_name)
                    if ext_template_config:
                        ext_resolved = self._resolve_template_composition(ext_template_config, user_config)
                        resolved = self.config_manager.merge_configs(resolved, ext_resolved)

        return resolved

    def _resolve_extension_dependencies(self, requirements: List[Dict[str, Any]], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve extension dependencies into configuration."""
        extensions_config = {'extensions': {}}

        for req in requirements:
            if isinstance(req, dict) and 'template' in req:
                ext_template_name = req['template']
                ext_template_config = self.template_discovery.get_template(ext_template_name)

                if ext_template_config:
                    # Generate default extension configuration
                    ext_variables = ext_template_config.get('variables', {})
                    if ext_variables:
                        # Apply variable interpolation for extension
                        interpolated = self.config_manager.interpolate_variables(ext_variables, user_config)
                        extensions_config['extensions'][ext_template_name] = interpolated

                    # Recursively resolve extension dependencies
                    ext_resolved = self._resolve_template_composition(ext_template_config, user_config)
                    extensions_config = self.config_manager.merge_configs(extensions_config, ext_resolved)

        return extensions_config

    def _generate_standalone_project(self, template_name: str, config_file: Optional[str], output_dir: str, **kwargs) -> Dict[str, Any]:
        """Generate a standalone project in the specified output directory."""

        output_path = Path(output_dir).resolve()

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Get template configuration
        template_config = self.template_discovery.get_template(template_name)
        if not template_config:
            raise ValueError(f"Template '{template_name}' not found")

        # Check if template supports standalone generation
        metadata = template_config.get('metadata', {})
        template_type = metadata.get('type')

        if template_type not in ['application', 'microservice']:
            raise ValueError(f"Template type '{template_type}' does not support standalone project generation")

        # Generate normal template configuration first
        config = self._build_configuration(template_name, config_file, kwargs)
        resolved_config = self._resolve_template_composition(template_config, config)

        # Create project structure in output directory
        self._create_project_structure(output_path, template_config, resolved_config)

        # Copy essential repository files to make it self-contained
        self._copy_repository_essentials(output_path)

        # Generate project-specific configuration
        project_playbook = self._generate_project_playbook(template_name, template_config, resolved_config, output_path)

        return project_playbook

    def _create_project_structure(self, output_path: Path, template_config: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Create the basic project structure in the output directory."""
        # Create standard directories
        (output_path / "source").mkdir(exist_ok=True)
        (output_path / "source" / "apps").mkdir(exist_ok=True)
        (output_path / "source" / "extensions").mkdir(exist_ok=True)
        (output_path / "tools").mkdir(exist_ok=True)
        (output_path / "templates").mkdir(exist_ok=True)

        # Copy template source files
        template_source_dir = template_config.get('template', {}).get('source_dir')
        if template_source_dir:
            src_path = self.repo_root / "templates" / template_source_dir
            if src_path.exists():
                dest_path = output_path / "source" / "apps" / config.get('application', {}).get('name', 'my_app')
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)

    def _copy_repository_essentials(self, output_path: Path) -> None:
        """Copy essential repository files for self-contained operation."""

        # Files to copy from the main repository
        essential_files = [
            'repo.sh',
            'repo.bat',
            'repo.toml',
            'premake5.lua'
        ]

        for file_name in essential_files:
            src_file = self.repo_root / file_name
            if src_file.exists():
                dest_file = output_path / file_name
                shutil.copy2(src_file, dest_file)

        # Copy tools directory (essential parts)
        tools_src = self.repo_root / "tools"
        tools_dest = output_path / "tools"
        if tools_src.exists():
            shutil.copytree(tools_src, tools_dest, dirs_exist_ok=True)

    def _generate_project_playbook(self, template_name: str, template_config: Dict[str, Any], config: Dict[str, Any], output_path: Path) -> Dict[str, Any]:
        """Generate playbook configuration for the standalone project."""
        # Create a modified playbook that references the local project structure
        playbook = {
            "project_info": {
                "name": config.get('application', {}).get('name', template_name),
                "display_name": config.get('application', {}).get('display_name', template_name),
                "version": config.get('application', {}).get('version', '0.1.0'),
                "template": template_name,
                "output_directory": str(output_path)
            },
            "standalone": True,
            "self_contained": True
        }

        return playbook

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
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: template_engine.py <command> [options]")
        print("")
        print("Commands:")
        print("  <template_name> [options]  Generate template (backward compatibility)")
        print("  docs [template_name]       Show template documentation")
        print("  list [--type=TYPE]         List available templates")
        print("")
        print("Options for generation:")
        print("  --config=<file>       Configuration file to use")
        print("  --name=<name>         Application/extension name")
        print("  --display-name=<name> Display name")
        print("  --version=<version>   Version (semver format)")
        print("  --output-dir=<dir>    Output directory for standalone projects")
        sys.exit(1)

    # Initialize engine
    repo_root = os.path.join(os.path.dirname(os.path.normpath(__file__)), "../..")
    engine = TemplateEngine(repo_root)

    command = sys.argv[1]

    try:
        if command == "docs":
            handle_docs_command(engine, sys.argv[2:])
        elif command == "list":
            handle_list_command(engine, sys.argv[2:])
        else:
            # Treat as template name for backward compatibility
            handle_generate_command(engine, command, sys.argv[2:])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_docs_command(engine: TemplateEngine, args: List[str]) -> None:
    """Handle 'docs' command."""
    if not args:
        print("Error: template name required for docs command")
        sys.exit(1)

    if args[0] == "--all":
        engine.print_all_templates_docs()
    else:
        template_name = args[0]
        docs = engine.format_template_docs(template_name)
        if docs:
            print(docs)
        else:
            print(f"Template '{template_name}' not found or has no documentation")
            sys.exit(1)

def handle_list_command(engine: TemplateEngine, args: List[str]) -> None:
    """Handle 'list' command."""
    template_type = None
    category = None

    for arg in args:
        if arg.startswith('--type='):
            template_type = arg.split('=', 1)[1]
        elif arg.startswith('--category='):
            category = arg.split('=', 1)[1]

    templates = engine.list_templates(template_type, category)

    if not templates:
        print("No templates found")
        return

    # Group by type for better display
    by_type = {}
    for name, config in templates.items():
        t_type = config.get('metadata', {}).get('type', 'unknown')
        if t_type not in by_type:
            by_type[t_type] = []
        by_type[t_type].append((name, config))

    for t_type in sorted(by_type.keys()):
        print(f"\n{t_type.upper()} Templates:")
        print("-" * 40)
        for name, config in sorted(by_type[t_type]):
            metadata = config.get('metadata', {})
            display_name = metadata.get('display_name', name)
            description = metadata.get('description', 'No description')
            print(f"  {name:<25} - {display_name}")
            if description != display_name:
                print(f"  {' ' * 27} {description[:60]}{'...' if len(description) > 60 else ''}")

def handle_generate_command(engine: TemplateEngine, template_name: str, args: List[str]) -> None:
    """Handle template generation command."""
    kwargs = {}
    config_file = None
    output_dir = None

    for arg in args:
        if arg.startswith('--config='):
            config_file = arg.split('=', 1)[1]
        elif arg.startswith('--output-dir='):
            output_dir = arg.split('=', 1)[1]
        elif arg.startswith('--'):
            if '=' in arg:
                key, value = arg[2:].split('=', 1)
                kwargs[key.replace('-', '_')] = value

    # Backward compatibility with positional arguments
    non_flag_args = [arg for arg in args if not arg.startswith('--')]
    if len(non_flag_args) > 0:
        kwargs['app_name'] = non_flag_args[0]
    if len(non_flag_args) > 1:
        kwargs['display_name'] = non_flag_args[1]
    if len(non_flag_args) > 2:
        kwargs['version'] = non_flag_args[2]

    # Generate template
    playback = engine.generate_template(template_name, config_file, output_dir, **kwargs)

    # Save to file
    playback_file = engine.save_playback_file(playback)

    # Print file path for repo.sh to use
    print(playback_file)


if __name__ == "__main__":
    main()