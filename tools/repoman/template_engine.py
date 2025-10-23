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
        print("Error: toml library not available.", file=sys.stderr)
        print("The template system requires the Python 'toml' package.", file=sys.stderr)
        print("", file=sys.stderr)
        print("This should have been installed automatically by repo.sh/repo.bat", file=sys.stderr)
        print("If you're seeing this error, please run:", file=sys.stderr)
        print("  make install-python-deps", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or install manually:", file=sys.stderr)
        print("  python -m pip install toml", file=sys.stderr)

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

        Raises:
            ValueError: If template is not found or configuration is invalid
            RuntimeError: If generation fails
        """

        try:
            # Handle output directory for standalone projects
            if output_dir:
                return self._generate_standalone_project(template_name, config_file, output_dir, **kwargs)

            # Load template configuration
            template_config = self.template_discovery.get_template(template_name)
            if template_config is None:
                available = list(self.template_discovery.discover_templates().keys())
                available_str = ', '.join(sorted(available[:10]))  # Show first 10
                if len(available) > 10:
                    available_str += f", ... ({len(available) - 10} more)"

                error_msg = f"Template '{template_name}' not found.\n"
                error_msg += f"Available templates: {available_str}\n"
                error_msg += "Use './repo.sh template list' to see all templates."
                raise ValueError(error_msg)

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

        except ValueError:
            raise  # Re-raise ValueError as-is
        except Exception as e:
            raise RuntimeError(f"Failed to generate template '{template_name}': {str(e)}")

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

                # Handle different TOML extension formats
                if isinstance(extensions, list):
                    # Simple list format: [[extensions]]
                    for ext_item in extensions:
                        if isinstance(ext_item, dict) and 'template' in ext_item:
                            ext_template = ext_item['template']
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
                    # Dictionary format: can have nested arrays like [[extensions.setup]]
                    for ext_key, ext_value in extensions.items():
                        if isinstance(ext_value, list):
                            # Nested array: [[extensions.setup]]
                            for ext_item in ext_value:
                                if isinstance(ext_item, dict) and 'template' in ext_item:
                                    ext_template = ext_item['template']
                                    ext_config_key = ext_template.replace('omni_', '').replace('kit_', '')
                                    custom_ext = config.get('extensions', {}).get(ext_config_key, {})

                                    # Generate extension configuration
                                    ext_suffix = ext_template.split('_')[-1]
                                    ext_configs[ext_template] = {
                                        "extension_name": custom_ext.get('name', f"{app_name}_{ext_suffix}"),
                                        "extension_display_name": custom_ext.get('display_name', f"{display_name} {ext_suffix.title()}"),
                                        "version": custom_ext.get('version', version)
                                    }
                        elif isinstance(ext_value, dict) and 'template' in ext_value:
                            # Simple dict entry
                            ext_template = ext_value['template']
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

        # Validate output directory
        if output_path.exists() and any(output_path.iterdir()):
            # Check if force_overwrite is enabled
            force_overwrite = kwargs.get('force_overwrite', False)
            if not force_overwrite:
                response = input(f"Directory '{output_path}' is not empty. Continue? [y/N]: ")
                if response.lower() != 'y':
                    raise ValueError("Aborted: output directory is not empty")

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
            error_msg = f"Template type '{template_type}' does not support standalone project generation.\n"
            error_msg += "Only 'application' and 'microservice' templates can be generated as standalone projects."
            raise ValueError(error_msg)

        print(f"Generating standalone {template_type} project from template '{template_name}'...", file=sys.stderr)

        try:
            # Generate normal template configuration first
            config = self._build_configuration(template_name, config_file, kwargs)
            resolved_config = self._resolve_template_composition(template_config, config)

            # Create project structure in output directory
            print(f"Creating project structure in {output_path}...", file=sys.stderr)
            self._create_project_structure(output_path, template_config, resolved_config)

            # Copy essential repository files to make it self-contained
            print("Copying build system and tools...", file=sys.stderr)
            self._copy_repository_essentials(output_path)

            # Generate project-specific configuration
            project_playbook = self._generate_project_playbook(template_name, template_config, resolved_config, output_path)

            # Create a README for the standalone project
            self._create_standalone_readme(output_path, template_name, template_config, resolved_config)

            print(f"\n✓ Standalone project generated successfully in: {output_path}", file=sys.stderr)
            print(f"\nTo build your project:", file=sys.stderr)
            print(f"  cd {output_path}", file=sys.stderr)
            print(f"  ./repo.sh build    # On Linux", file=sys.stderr)
            print(f"  .\\repo.bat build   # On Windows", file=sys.stderr)

            return project_playbook

        except Exception as e:
            print(f"\n❌ Failed to generate standalone project: {e}", file=sys.stderr)
            # Clean up on failure
            if output_path.exists() and not any(output_path.iterdir()):
                output_path.rmdir()
            raise

    def _create_project_structure(self, output_path: Path, template_config: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Create the basic project structure in the output directory."""
        # Create standard directories
        directories = [
            "source",
            "_build/apps",
            "source/extensions",
            "tools",
            "tools/packman",
            "tools/repoman",
            "templates",
            "templates/config",
            "_build",
            "_compiler",
            "_repo"
        ]

        for directory in directories:
            (output_path / directory).mkdir(parents=True, exist_ok=True)

        # Determine if this is an application or extension template
        template_type = template_config.get('metadata', {}).get('type', 'extension')

        # Copy template source files to appropriate location
        template_source_dir = template_config.get('template', {}).get('source_dir')
        if template_source_dir:
            src_path = self.repo_root / "templates" / template_source_dir
            if src_path.exists():
                if template_type in ['application', 'microservice']:
                    # For applications, copy to apps directory
                    app_name = config.get('application', {}).get('name', 'my_app')
                    dest_path = output_path / "source" / "apps" / app_name
                else:
                    # For extensions, copy to extensions directory
                    ext_name = config.get('extension', {}).get('name', 'my_extension')
                    dest_path = output_path / "source" / "extensions" / ext_name

                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)

        # Copy template configuration files for reference
        template_file = Path(template_config.get('_template_file', ''))
        if template_file.exists():
            dest_template_dir = output_path / "templates" / template_type
            dest_template_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template_file, dest_template_dir / "template.toml")

    def _copy_repository_essentials(self, output_path: Path) -> None:
        """Copy essential repository files for self-contained operation."""

        try:
            # Files to copy from the main repository
            essential_files = [
                'repo.sh',
                'repo.bat',
                'repo.toml',
                'premake5.lua',
                'repo_tools.toml',
                '.editorconfig',
                'LICENSE'
            ]

            for file_name in essential_files:
                src_file = self.repo_root / file_name
                if src_file.exists():
                    dest_file = output_path / file_name
                    shutil.copy2(src_file, dest_file)
                    # Make scripts executable on Unix-like systems
                    if file_name.endswith('.sh'):
                        os.chmod(dest_file, 0o755)

            # Copy essential tools directories
            essential_tool_dirs = [
                ('tools/packman', True),  # Required for build system
                ('tools/repoman', True),  # Required for template system
                ('tools/package.sh', False),  # Packaging script
                ('tools/package.bat', False)  # Windows packaging script
            ]

            for tool_path, is_dir in essential_tool_dirs:
                src_path = self.repo_root / tool_path
                dest_path = output_path / tool_path

                if src_path.exists():
                    if is_dir:
                        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                        # Make shell scripts executable
                        for sh_file in dest_path.glob('**/*.sh'):
                            os.chmod(sh_file, 0o755)
                    else:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dest_path)
                        if tool_path.endswith('.sh'):
                            os.chmod(dest_path, 0o755)

            # Copy minimal template system files for the project to be self-contained
            templates_src = self.repo_root / "templates"
            templates_dest = output_path / "templates"

            # Copy the entire templates directory so replay can find template files
            if templates_src.exists():
                shutil.copytree(templates_src, templates_dest, dirs_exist_ok=True)

        except Exception as e:
            print(f"Warning: Some files could not be copied: {e}", file=sys.stderr)

    def _generate_project_playbook(self, template_name: str, template_config: Dict[str, Any], config: Dict[str, Any], output_path: Path) -> Dict[str, Any]:
        """Generate playbook configuration for the standalone project."""
        # Generate the normal playback for the template
        playback = self._generate_playback(template_name, template_config, config)

        # Add standalone project metadata
        playback["_standalone_project"] = {
            "name": config.get('application', {}).get('name', template_name),
            "display_name": config.get('application', {}).get('display_name', template_name),
            "version": config.get('application', {}).get('version', '0.1.0'),
            "template": template_name,
            "output_directory": str(output_path),
            "self_contained": True
        }

        return playback

    def _create_standalone_readme(self, output_path: Path, template_name: str, template_config: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Create a README file for the standalone project."""
        metadata = template_config.get('metadata', {})
        documentation = template_config.get('documentation', {})
        template_type = metadata.get('type', 'application')

        # Get project details
        if template_type in ['application', 'microservice']:
            name = config.get('application', {}).get('name', template_name)
            display_name = config.get('application', {}).get('display_name', template_name)
            version = config.get('application', {}).get('version', '0.1.0')
        else:
            name = config.get('extension', {}).get('name', template_name)
            display_name = config.get('extension', {}).get('display_name', template_name)
            version = config.get('extension', {}).get('version', '0.1.0')

        readme_content = f"""# {display_name}

## Overview

This is a standalone {template_type} project generated from the '{template_name}' template.

{documentation.get('overview', 'A Kit SDK-based project for the NVIDIA Omniverse platform.')}

## Project Information

- **Name**: {name}
- **Version**: {version}
- **Template**: {template_name}
- **Type**: {template_type.title()}

## Prerequisites

- **Operating System**: Windows 10/11 or Linux (Ubuntu 22.04 or newer)
- **GPU**: NVIDIA RTX capable GPU (RTX 3070 or better recommended)
- **Driver**: Minimum 537.58
- **Git**: For version control
- **Git LFS**: For managing large files

## Building the Project

### Linux
```bash
./repo.sh build
```

### Windows
```powershell
.\\repo.bat build
```

## Running the Project

### Linux
```bash
./repo.sh launch
```

### Windows
```powershell
.\\repo.bat launch
```

## Available Commands

- `build` - Build the project
- `launch` - Launch the application
- `test` - Run tests
- `package` - Package for distribution
- `clean` - Clean build artifacts

## Project Structure

```
.
├── source/              # Source code
│   ├── apps/           # Application definitions
│   └── extensions/     # Extension modules
├── tools/              # Build and development tools
├── _build/             # Build output (generated)
├── _compiler/          # Compiler artifacts (generated)
└── _repo/              # Repository cache (generated)
```

## Development

This project includes all necessary build tools and dependencies to work as a standalone repository. You can:

1. Initialize a new git repository: `git init`
2. Add your changes: `git add .`
3. Commit: `git commit -m "Initial commit"`
4. Push to your remote repository

## Documentation

For more information about the Omniverse Kit SDK and development practices, visit:
- [Omniverse Kit SDK Manual](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/index.html)
- [Kit App Template Documentation](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html)

## License

This project is based on the NVIDIA Omniverse Kit SDK and is subject to the NVIDIA Software License Agreement and Product-Specific Terms for NVIDIA Omniverse.

---

Generated with the Kit App Template system
"""

        readme_path = output_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)

    def save_playback_file(self, playback: Dict[str, Any]) -> str:
        """Save playback configuration to a temporary file."""
        # Use text mode explicitly for cross-platform compatibility
        fd, temp_path = tempfile.mkstemp(suffix='.toml', text=True)
        try:
            if HAS_TOMLI_W:
                # tomli_w expects a binary file - close the text fd first
                os.close(fd)
                with open(temp_path, 'wb') as bf:
                    tomli_w.dump(playback, bf)
            elif HAS_TOML:
                with os.fdopen(fd, 'w') as f:
                    toml.dump(playback, f)
            else:
                # Manual TOML writing
                with os.fdopen(fd, 'w') as f:
                    self._write_toml_manual(f, playback)
        except Exception as e:
            try:
                os.close(fd)
            except:
                pass  # fd might already be closed
            raise e

        return temp_path

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
        print("  <template_name> [options]  Generate template")
        print("  docs [template_name]       Show template documentation")
        print("  list [--type=TYPE]         List available templates")
        print("")
        print("Options for generation:")
        print("  --name=<name>         Application/extension name (required)")
        print("  --display-name=<name> Display name (required)")
        print("  --version=<version>   Version in semver format (required)")
        print("  --config=<file>       Configuration file to use")
        print("  --output-dir=<dir>    Output directory for standalone projects")
        print("  --add-layers          Add application layers (e.g., streaming)")
        print("  --layers=<l1,l2>      Comma-separated list of layer templates")
        print("  --accept-license      Accept license terms non-interactively")
        print("")
        print("Examples:")
        print("  # Simple application")
        print("  template_engine.py kit_base_editor --name=my.app --display-name=\"My App\" --version=1.0.0")
        print("")
        print("  # With streaming layer")
        print("  template_engine.py kit_base_editor --name=my.app --display-name=\"My App\" \\")
        print("    --version=1.0.0 --layers=omni_default_streaming")
        print("")
        print("  # Accept license non-interactively (for CI/CD)")
        print("  template_engine.py kit_base_editor --name=my.app --display-name=\"My App\" \\")
        print("    --version=1.0.0 --accept-license")
        sys.exit(1)

    # Initialize engine with OS-independent path handling
    script_dir = Path(__file__).resolve().parent
    repo_root = str(script_dir.parent.parent)
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
    json_output = False

    for arg in args:
        if arg.startswith('--type='):
            template_type = arg.split('=', 1)[1]
        elif arg.startswith('--category='):
            category = arg.split('=', 1)[1]
        elif arg == '--json':
            json_output = True

    templates = engine.list_templates(template_type, category)

    if not templates:
        if json_output:
            import json as json_module
            print(json_module.dumps({"status": "success", "count": 0, "templates": []}, indent=2))
        else:
            print("No templates found")
        return

    # JSON output mode
    if json_output:
        import json as json_module
        template_list = []
        for name, config in templates.items():
            metadata = config.get('metadata', {})
            template_list.append({
                "name": name,
                "display_name": metadata.get('display_name', name),
                "type": metadata.get('type', 'unknown'),
                "description": metadata.get('description', ''),
                "category": metadata.get('category', '')
            })
        result = {
            "status": "success",
            "count": len(template_list),
            "templates": sorted(template_list, key=lambda t: (t['type'], t['name']))
        }
        print(json_module.dumps(result, indent=2))
        return

    # Normal output mode - Group by type for better display
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
    add_layers = False
    layers = []
    accept_license = False
    json_output = False
    verbose = False
    quiet = False

    for arg in args:
        if arg.startswith('--config='):
            config_file = arg.split('=', 1)[1]
        elif arg.startswith('--output-dir='):
            output_dir = arg.split('=', 1)[1]
        elif arg == '--add-layers':
            add_layers = True
        elif arg.startswith('--layers='):
            layers_str = arg.split('=', 1)[1]
            layers = [l.strip() for l in layers_str.split(',')]
            add_layers = True  # Implies --add-layers
        elif arg == '--accept-license':
            accept_license = True
        elif arg == '--json':
            json_output = True
        elif arg == '--verbose':
            verbose = True
        elif arg == '--quiet':
            quiet = True
        elif arg.startswith('--'):
            if '=' in arg:
                key, value = arg[2:].split('=', 1)
                kwargs[key.replace('-', '_')] = value

    # Handle layers
    if add_layers:
        kwargs['add_layers'] = 'Yes'
        if layers:
            kwargs['layers'] = layers

    # Backward compatibility with positional arguments
    non_flag_args = [arg for arg in args if not arg.startswith('--')]
    if len(non_flag_args) > 0:
        kwargs['app_name'] = non_flag_args[0]
    if len(non_flag_args) > 1:
        kwargs['display_name'] = non_flag_args[1]
    if len(non_flag_args) > 2:
        kwargs['version'] = non_flag_args[2]

    # Check license with auto-accept if flag provided
    from license_manager import check_and_prompt_license
    if not check_and_prompt_license(auto_accept=accept_license):
        if json_output:
            import json as json_module
            error_data = {
                "status": "error",
                "error": "License terms must be accepted to use templates",
                "code": 1
            }
            print(json_module.dumps(error_data, indent=2))
        else:
            print("Error: License terms must be accepted to use templates.", file=sys.stderr)
        sys.exit(1)

    # Note: --output-dir can be used to create standalone projects
    # By default (when output_dir is None), templates are created in _build/apps/

    try:
        # Generate template
        playback = engine.generate_template(template_name, config_file, output_dir, **kwargs)

        # Save to file
        playback_file = engine.save_playback_file(playback)

        # Always print playback file path first (required for repo_dispatcher)
        print(playback_file)
        
        # Output additional information based on mode
        if json_output:
            # JSON output mode - print JSON to stderr so repo_dispatcher ignores it
            # but tests/users can still capture it
            import json as json_module
            result_data = {
                "status": "success",
                "playback_file": playback_file,
                "template_name": template_name,
                "name": kwargs.get('app_name', kwargs.get('name', 'unknown')),
                "path": str(playback.get('output_path', '')) if isinstance(playback, dict) else ''
            }
            print(json_module.dumps(result_data, indent=2), file=sys.stderr)
        elif verbose:
            # Verbose mode - add extra details to stderr
            print(f"[VERBOSE] Template: {template_name}", file=sys.stderr)
            print(f"[VERBOSE] Playback file: {playback_file}", file=sys.stderr)
            if kwargs.get('app_name'):
                print(f"[VERBOSE] Application name: {kwargs['app_name']}", file=sys.stderr)
        # Quiet mode and normal mode just print playback file (already done above)

    except Exception as e:
        # Handle errors
        if json_output:
            import json as json_module
            error_data = {
                "status": "error",
                "error": str(e),
                "template_name": template_name,
                "code": 1
            }
            print(json_module.dumps(error_data, indent=2))
        else:
            print(f"Error generating template: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
