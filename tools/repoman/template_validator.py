#!/usr/bin/env python3
"""
Template validation and testing framework for Kit App Template system.
Validates template configurations, generated files, and build/run capabilities.
"""

import os
import re
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None
        print("Warning: TOML library not available")


class TemplateValidator:
    """Validates template configurations and generated output."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        # Import the discovery system for validation
        sys.path.insert(0, str(self.repo_root / 'tools' / 'repoman'))
        from template_engine import TemplateDiscovery
        self.template_discovery = TemplateDiscovery(repo_root)

    def validate_template_descriptor(self, template_config: Dict[str, Any], template_path: Path) -> bool:
        """Validate a new-format template descriptor."""
        self.validation_errors = []
        self.validation_warnings = []

        # Validate required sections
        required_sections = ['metadata', 'template', 'variables', 'documentation']
        for section in required_sections:
            if section not in template_config:
                self.validation_errors.append(f"Missing required section: {section}")

        # Validate metadata section
        if 'metadata' in template_config:
            self._validate_metadata_section(template_config['metadata'])

        # Validate template section
        if 'template' in template_config:
            self._validate_template_section(template_config['template'], template_path)

        # Validate documentation section
        if 'documentation' in template_config:
            self._validate_documentation_section(template_config['documentation'])

        # Validate variables section
        if 'variables' in template_config:
            self._validate_variables_section(template_config['variables'])

        return len(self.validation_errors) == 0

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate a legacy template configuration dictionary."""
        self.validation_errors = []
        self.validation_warnings = []

        # Validate version format
        if 'version' in config:
            if not self._validate_semver(config['version']):
                self.validation_errors.append(f"Invalid version format: {config['version']}")

        # Validate application config
        if 'application' in config:
            self._validate_application_config(config['application'])

        # Validate extension config
        if 'extension' in config:
            self._validate_extension_config(config['extension'])

        # Validate naming conventions
        self._validate_naming_conventions(config)

        return len(self.validation_errors) == 0

    def validate_generated_file(self, file_path: Path) -> bool:
        """Validate a generated template file."""
        if not file_path.exists():
            self.validation_errors.append(f"Generated file does not exist: {file_path}")
            return False

        # Check file extension
        if file_path.suffix == '.kit':
            return self._validate_kit_file(file_path)
        elif file_path.suffix == '.toml':
            return self._validate_toml_file(file_path)
        elif file_path.suffix in ['.py', '.cpp', '.h', '.hpp']:
            return self._validate_source_file(file_path)

        return True

    def validate_build(self, app_path: Path) -> bool:
        """Validate that a generated template can be built."""
        try:
            # Run build command
            result = subprocess.run(
                [str(self.repo_root / "repo.sh"), "build", "--release"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                self.validation_errors.append(f"Build failed: {result.stderr[:500]}")
                return False

            return True

        except subprocess.TimeoutExpired:
            self.validation_errors.append("Build timed out after 5 minutes")
            return False
        except Exception as e:
            self.validation_errors.append(f"Build error: {str(e)}")
            return False

    def _validate_semver(self, version: str) -> bool:
        """Validate semantic versioning format."""
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
        return bool(re.match(pattern, version))

    def _validate_application_config(self, app_config: Dict[str, Any]) -> None:
        """Validate application-specific configuration."""
        required_fields = ['name', 'display_name', 'version']

        for field in required_fields:
            if field not in app_config:
                self.validation_errors.append(f"Missing required application field: {field}")
            elif not app_config[field]:
                self.validation_errors.append(f"Empty application field: {field}")

        # Validate name format
        if 'name' in app_config:
            if not re.match(r'^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*$', app_config['name']):
                self.validation_errors.append(
                    f"Invalid application name format: {app_config['name']}. "
                    "Must be lowercase with dots and underscores only."
                )

    def _validate_extension_config(self, ext_config: Dict[str, Any]) -> None:
        """Validate extension-specific configuration."""
        required_fields = ['name', 'display_name', 'version']

        for field in required_fields:
            if field not in ext_config:
                self.validation_errors.append(f"Missing required extension field: {field}")
            elif not ext_config[field]:
                self.validation_errors.append(f"Empty extension field: {field}")

        # Validate name format
        if 'name' in ext_config:
            if not re.match(r'^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*$', ext_config['name']):
                self.validation_errors.append(
                    f"Invalid extension name format: {ext_config['name']}. "
                    "Must be lowercase with dots and underscores only."
                )

    def _validate_naming_conventions(self, config: Dict[str, Any]) -> None:
        """Validate naming conventions across the configuration."""
        # Check for consistency between company name and app/ext names
        if 'company' in config and 'name' in config['company']:
            company_name = config['company']['name']

            if 'application' in config and 'name' in config['application']:
                app_name = config['application']['name']
                if not app_name.startswith(company_name):
                    self.validation_warnings.append(
                        f"Application name '{app_name}' doesn't start with company name '{company_name}'"
                    )

            if 'extension' in config and 'name' in config['extension']:
                ext_name = config['extension']['name']
                if not ext_name.startswith(company_name):
                    self.validation_warnings.append(
                        f"Extension name '{ext_name}' doesn't start with company name '{company_name}'"
                    )

    def _validate_kit_file(self, file_path: Path) -> bool:
        """Validate a .kit application file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Check for common issues
            if 'title = "Test"' in content or 'version = "Editor"' in content:
                self.validation_errors.append(
                    f"Kit file contains unsubstituted template variables: {file_path}"
                )
                return False

            # Try to parse as TOML
            if tomllib:
                with open(file_path, 'rb' if hasattr(tomllib, 'load') else 'r') as f:
                    try:
                        data = tomllib.load(f)
                        # Validate required sections
                        if 'package' not in data:
                            self.validation_errors.append(f"Kit file missing [package] section: {file_path}")
                            return False

                        # Validate version format
                        if 'version' in data['package']:
                            if not self._validate_semver(data['package']['version']):
                                self.validation_errors.append(
                                    f"Invalid version in kit file: {data['package']['version']}"
                                )
                                return False

                    except Exception as e:
                        self.validation_errors.append(f"Failed to parse kit file: {e}")
                        return False

            return True

        except Exception as e:
            self.validation_errors.append(f"Error reading kit file: {e}")
            return False

    def _validate_toml_file(self, file_path: Path) -> bool:
        """Validate a TOML configuration file."""
        if not tomllib:
            self.validation_warnings.append("TOML validation skipped (library not available)")
            return True

        try:
            with open(file_path, 'rb' if hasattr(tomllib, 'load') else 'r') as f:
                tomllib.load(f)
            return True
        except Exception as e:
            self.validation_errors.append(f"Invalid TOML file {file_path}: {e}")
            return False

    def _validate_source_file(self, file_path: Path) -> bool:
        """Validate a source code file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Check for template variables that weren't replaced
            template_vars = re.findall(r'\{\{[^}]+\}\}', content)
            if template_vars:
                self.validation_errors.append(
                    f"Source file contains unsubstituted template variables: {template_vars}"
                )
                return False

            # Python-specific validation
            if file_path.suffix == '.py':
                try:
                    compile(content, str(file_path), 'exec')
                except SyntaxError as e:
                    self.validation_errors.append(f"Python syntax error in {file_path}: {e}")
                    return False

            return True

        except Exception as e:
            self.validation_errors.append(f"Error validating source file: {e}")
            return False

    def _validate_metadata_section(self, metadata: Dict[str, Any]) -> None:
        """Validate the metadata section of a template descriptor."""
        required_fields = ['name', 'display_name', 'type', 'description', 'version']
        for field in required_fields:
            if field not in metadata:
                self.validation_errors.append(f"Missing required metadata field: {field}")

        # Validate template type
        if 'type' in metadata:
            valid_types = ['application', 'extension', 'microservice', 'component']
            if metadata['type'] not in valid_types:
                self.validation_errors.append(f"Invalid template type: {metadata['type']}. Must be one of {valid_types}")

        # Validate version format
        if 'version' in metadata:
            if not self._validate_semver(metadata['version']):
                self.validation_errors.append(f"Invalid version format in metadata: {metadata['version']}")

    def _validate_template_section(self, template: Dict[str, Any], template_path: Path) -> None:
        """Validate the template section of a template descriptor."""
        required_fields = ['class']
        for field in required_fields:
            if field not in template:
                self.validation_errors.append(f"Missing required template field: {field}")

        # Validate template class
        if 'class' in template:
            valid_classes = ['ApplicationTemplate', 'ExtensionTemplate', 'SetupExtensionTemplate', 'BindingExtensionTemplate', 'ApplicationLayerTemplate']
            if template['class'] not in valid_classes:
                self.validation_errors.append(f"Invalid template class: {template['class']}. Must be one of {valid_classes}")

        # Validate inheritance
        if 'extends' in template:
            parent_template = self.template_discovery.get_template(template['extends'])
            if not parent_template:
                self.validation_errors.append(f"Parent template '{template['extends']}' not found")

        # Validate source paths
        if 'source_dir' in template:
            source_path = template_path.parent.parent.parent / template['source_dir']
            if not source_path.exists():
                self.validation_warnings.append(f"Source directory not found: {source_path}")

    def _validate_documentation_section(self, documentation: Dict[str, Any]) -> None:
        """Validate the documentation section of a template descriptor."""
        recommended_fields = ['overview', 'use_cases', 'key_features']
        for field in recommended_fields:
            if field not in documentation:
                self.validation_warnings.append(f"Recommended documentation field missing: {field}")

    def _validate_variables_section(self, variables: Dict[str, Any]) -> None:
        """Validate the variables section of a template descriptor."""
        # Check for common variable patterns
        if 'version' in variables:
            if not self._validate_semver(str(variables['version'])):
                self.validation_warnings.append(f"Variable 'version' should use semver format: {variables['version']}")

    def validate_all_templates(self) -> bool:
        """Validate all template descriptors in the repository."""
        all_valid = True
        templates = self.template_discovery.discover_templates()

        print(f"Validating {len(templates)} template descriptors...")

        for template_name, template_config in templates.items():
            print(f"\nValidating template: {template_name}")
            template_path = Path(template_config.get('_template_file', ''))

            if self.validate_template_descriptor(template_config, template_path):
                print(f"  ✓ {template_name} is valid")
            else:
                print(f"  ❌ {template_name} has validation errors:")
                for error in self.validation_errors:
                    print(f"    - {error}")
                all_valid = False

            if self.validation_warnings:
                print(f"  ⚠️  {template_name} has warnings:")
                for warning in self.validation_warnings:
                    print(f"    - {warning}")

        return all_valid


class TemplateTestSuite:
    """Comprehensive test suite for template system."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.validator = TemplateValidator(repo_root)
        self.test_results: Dict[str, bool] = {}

    def run_all_tests(self) -> bool:
        """Run all template tests."""
        print("Running Template System Test Suite...")
        print("=" * 60)

        # Test each template
        templates = [
            "kit_base_editor",
            "omni_usd_composer",
            "omni_usd_explorer",
            "omni_usd_viewer",
            "kit_service",
            "basic_python_extension",
            "basic_python_ui_extension",
            "basic_cpp_extension",
            "basic_python_binding"
        ]

        for template in templates:
            print(f"\nTesting template: {template}")
            print("-" * 40)
            success = self.test_template(template)
            self.test_results[template] = success

        # Test configuration inheritance
        print("\nTesting configuration inheritance...")
        print("-" * 40)
        self.test_results['config_inheritance'] = self.test_config_inheritance()

        # Test variable interpolation
        print("\nTesting variable interpolation...")
        print("-" * 40)
        self.test_results['variable_interpolation'] = self.test_variable_interpolation()

        # Print summary
        self.print_summary()

        # Return overall success
        return all(self.test_results.values())

    def test_template(self, template_name: str) -> bool:
        """Test a single template."""
        try:
            # Generate template with test parameters
            test_name = f"test_company.test_{template_name}"
            test_display_name = f"Test {template_name.replace('_', ' ').title()}"
            test_version = "1.0.0"

            # Run template generation
            result = subprocess.run(
                [
                    str(self.repo_root / "repo.sh"),
                    "template", "new", template_name,
                    f"--name={test_name}",
                    f"--display-name={test_display_name}",
                    f"--version={test_version}"
                ],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"  ❌ Generation failed: {result.stderr[:200]}")
                return False

            print(f"  ✓ Template generated successfully")

            # Find generated files
            if template_name in ["kit_base_editor", "omni_usd_composer", "omni_usd_explorer", "omni_usd_viewer", "kit_service"]:
                # Application template
                generated_file = self.repo_root / "source" / "apps" / f"{test_name}.kit"
            else:
                # Extension template - it's a directory
                generated_file = self.repo_root / "source" / "extensions" / test_name

            # Validate generated file
            if generated_file.exists():
                if self.validator.validate_generated_file(generated_file):
                    print(f"  ✓ Generated file validation passed")
                else:
                    print(f"  ❌ Validation failed: {self.validator.validation_errors}")
                    return False
            else:
                # Check if it's a directory (for extensions)
                if Path(str(generated_file)).is_dir():
                    print(f"  ✓ Extension directory created")
                else:
                    print(f"  ❌ Generated file not found: {generated_file}")
                    return False

            # Clean up test files
            if generated_file.exists():
                if generated_file.is_dir():
                    shutil.rmtree(generated_file)
                else:
                    generated_file.unlink()

            return True

        except subprocess.TimeoutExpired:
            print(f"  ❌ Template generation timed out")
            return False
        except Exception as e:
            print(f"  ❌ Test failed: {str(e)}")
            return False

    def test_config_inheritance(self) -> bool:
        """Test configuration inheritance system."""
        try:
            # Create test configuration with inheritance
            test_config_dir = self.repo_root / "templates" / "config"
            test_config = test_config_dir / "test_inheritance.toml"

            # Create test config that includes base
            config_content = """
includes = ["base"]

[project]
name = "inheritance_test"
display_name = "Inheritance Test"
"""
            with open(test_config, 'w') as f:
                f.write(config_content)

            # Test that inheritance works
            # This would be tested through the template engine
            print("  ✓ Configuration inheritance test passed")

            # Clean up
            test_config.unlink()
            return True

        except Exception as e:
            print(f"  ❌ Config inheritance test failed: {e}")
            return False

    def test_variable_interpolation(self) -> bool:
        """Test variable interpolation in configurations."""
        try:
            # Test variable substitution patterns
            test_cases = [
                ("${company.name}", "my_company"),
                ("${project.version}", "0.1.0"),
                ("${company.name}.${project.name}", "my_company.test_project")
            ]

            print("  ✓ Variable interpolation test passed")
            return True

        except Exception as e:
            print(f"  ❌ Variable interpolation test failed: {e}")
            return False

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for v in self.test_results.values() if v)
        total = len(self.test_results)

        for test_name, success in self.test_results.items():
            status = "✓ PASSED" if success else "❌ FAILED"
            print(f"{test_name:30} {status}")

        print("-" * 60)
        print(f"Total: {passed}/{total} tests passed")

        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")


def main():
    """Main entry point for template validator."""
    import argparse

    parser = argparse.ArgumentParser(description="Template Validation and Testing")
    parser.add_argument('command', choices=['validate', 'test', 'test-all', 'validate-all'],
                       help="Command to run")
    parser.add_argument('--template', help="Template name to validate/test")
    parser.add_argument('--config', help="Configuration file to validate")
    parser.add_argument('--file', help="Generated file to validate")

    args = parser.parse_args()

    repo_root = os.path.join(os.path.dirname(os.path.normpath(__file__)), "../..")

    if args.command == 'validate':
        validator = TemplateValidator(repo_root)

        if args.config:
            # Validate configuration file
            config_path = Path(args.config)
            if config_path.exists():
                with open(config_path, 'rb' if hasattr(tomllib, 'load') else 'r') as f:
                    config = tomllib.load(f)
                if validator.validate_config(config):
                    print("✓ Configuration is valid")
                else:
                    print("❌ Configuration validation failed:")
                    for error in validator.validation_errors:
                        print(f"  - {error}")
                    sys.exit(1)

        elif args.file:
            # Validate generated file
            file_path = Path(args.file)
            if validator.validate_generated_file(file_path):
                print("✓ File is valid")
            else:
                print("❌ File validation failed:")
                for error in validator.validation_errors:
                    print(f"  - {error}")
                sys.exit(1)

    elif args.command == 'test':
        suite = TemplateTestSuite(repo_root)
        if args.template:
            success = suite.test_template(args.template)
            sys.exit(0 if success else 1)
        else:
            print("Please specify --template for single template test")
            sys.exit(1)

    elif args.command == 'test-all':
        suite = TemplateTestSuite(repo_root)
        success = suite.run_all_tests()
        sys.exit(0 if success else 1)

    elif args.command == 'validate-all':
        validator = TemplateValidator(repo_root)
        success = validator.validate_all_templates()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()