# Kit App Template System Documentation

## Overview

The Kit App Template System provides a fully data-driven, non-interactive approach for generating Kit applications and extensions. This system enables teams to create consistent, validated templates using configuration files and command-line parameters.

## Quick Start

### Basic Usage

Generate a Kit application or extension using the command line:

```bash
# Generate a Kit Base Editor application
./repo.sh template new kit_base_editor --name=my_company.my_editor --display-name="My Editor" --version=1.0.0

# Generate a Python extension
./repo.sh template new basic_python_extension --name=my_company.my_extension --display-name="My Extension" --version=1.0.0
```

### Using Configuration Files

Create a project configuration file and use it to generate templates:

```bash
# Generate using a project configuration file
./repo.sh template new omni_usd_viewer --config=my-project.toml
```

## Available Templates

### Application Templates

- **kit_base_editor** - A foundation for a base editor application
- **omni_usd_composer** - USD Composer application with setup extension
- **omni_usd_explorer** - USD Explorer application with setup extension
- **omni_usd_viewer** - USD Viewer application with messaging and setup extensions
- **kit_service** - Kit microservice application

### Extension Templates

- **basic_python_extension** - Basic Python extension
- **basic_python_ui_extension** - Python extension with UI components
- **basic_cpp_extension** - Basic C++ extension
- **basic_python_binding** - C++ extension with Python bindings

## Configuration System

### User Configuration

Create a user configuration file in one of these locations:
- `~/.omni/kit-app-template/user.toml`
- `~/.config/omni/kit-app-template.toml`
- `./user-config.toml` (in repository root)

Example user configuration:

```toml
[user]
name = "John Developer"
email = "john.developer@company.com"

[company]
name = "my_company"
display_name = "My Company"
domain = "mycompany.com"

[project]
author = "${user.name}"
copyright = "Copyright (c) 2024 ${company.display_name}. All rights reserved."
license = "Proprietary"
```

### Project Configuration

Create project-specific configurations that include base configurations:

```toml
# my-project.toml
includes = ["base"]  # Include base configuration

[company]
name = "awesome_corp"
display_name = "Awesome Corporation"

[project]
name = "super_viewer"
display_name = "Super Viewer"
version = "2.0.0"
description = "An amazing USD viewer application"

[application]
name = "${company.name}.${project.name}"  # Variable interpolation
display_name = "${project.display_name}"
version = "${project.version}"

# Extension overrides for USD Viewer template
[extensions.viewer_setup]
name = "${company.name}.${project.name}_setup"
display_name = "${project.display_name} Setup"
version = "${project.version}"
```

### Configuration Inheritance

Configurations can include other configurations using the `includes` directive:

```toml
includes = ["base", "company_defaults"]  # Include multiple base configs

[project]
# Override specific values
name = "my_project"
```

### Variable Interpolation

Use variable references in configurations:

```toml
[company]
name = "acme"

[application]
name = "${company.name}.${project.name}"  # Resolves to: acme.my_app
```

Environment variables can also be referenced:

```toml
[paths]
output = "${env.HOME}/projects/${project.name}"
```

## Template Validation

### Automatic Validation

All generated templates are automatically validated for:
- Semantic versioning compliance
- Required field presence
- Naming convention adherence
- TOML/JSON syntax correctness
- Template variable substitution

### Manual Validation

Run validation on configurations or generated files:

```bash
# Validate a configuration file
python3 tools/repoman/template_validator.py validate --config=my-project.toml

# Validate a generated file
python3 tools/repoman/template_validator.py validate --file=source/apps/my_app.kit

# Test a specific template
python3 tools/repoman/template_validator.py test --template=kit_base_editor

# Run full test suite
python3 tools/repoman/template_validator.py test-all
```

## Advanced Features

### Batch Template Generation

Generate multiple templates using a configuration file:

```toml
# batch-config.toml
[templates.app1]
type = "kit_base_editor"
name = "company.editor"
display_name = "Company Editor"
version = "1.0.0"

[templates.app2]
type = "omni_usd_viewer"
name = "company.viewer"
display_name = "Company Viewer"
version = "1.0.0"
```

### Custom Template Directories

Configure custom template locations in `templates/templates.toml`:

```toml
[templates."custom_template"]
class = "ApplicationTemplate"
name = "Custom Application"
url = "file:///path/to/custom/templates"
subpath = "apps/custom"
```

## Build and Run

After generating a template, build and run it:

```bash
# Build the project
./repo.sh build

# Run an application
./repo.sh launch --app source/apps/my_company.my_editor.kit

# Run with debugging
./repo.sh launch --app source/apps/my_company.my_editor.kit --verbose
```

## Testing Generated Templates

### Validation Pipeline

1. **Pre-generation**: Validates input configuration
2. **Post-generation**: Validates generated files
3. **Build validation**: Ensures templates compile
4. **Runtime validation**: Tests that applications run

### Running Tests

```bash
# Run all project tests (recommended)
./repo.sh test

# Run only template system tests
./repo.sh test templates

# Test all templates directly
python3 tools/repoman/template_validator.py test-all

# Test specific template
python3 tools/repoman/template_validator.py test --template=kit_base_editor

# Validate build capability
./repo.sh build --release
```

## Migration from Interactive System

### Old Interactive Method (Deprecated)

```bash
# Old method prompted for user input
./repo.sh template new
# Then answered questions interactively
```

### New Data-Driven Method

```bash
# New method - all parameters provided upfront
./repo.sh template new kit_base_editor \
    --name=my_company.my_app \
    --display-name="My App" \
    --version=1.0.0

# Or using configuration file
./repo.sh template new kit_base_editor --config=project.toml
```

## Best Practices

### 1. Use Configuration Files

Create reusable configuration files for consistency:
- User configs for personal defaults
- Company configs for organizational standards
- Project configs for specific applications

### 2. Follow Naming Conventions

- Application names: `company.product` (lowercase, dot-separated)
- Extension names: `company.extension_name` (lowercase, underscores)
- Display names: "Product Name" (title case)
- Versions: Semantic versioning (e.g., 1.0.0)

### 3. Validate Before Building

Always validate templates before attempting to build:

```bash
# Generate and validate
./repo.sh template new kit_base_editor --name=test.app --version=1.0.0
python3 tools/repoman/template_validator.py validate --file=source/apps/test.app.kit

# Then build
./repo.sh build
```

### 4. Version Control Configuration

Track your configuration files in version control:

```
project/
├── .gitignore
├── project-config.toml      # Project-specific config
├── templates/
│   └── config/
│       ├── base.toml         # Base configuration
│       └── company.toml      # Company defaults
```

## Troubleshooting

### Common Issues

1. **"Invalid version format" error**
   - Ensure version follows semantic versioning (e.g., 1.0.0)
   - Don't use non-numeric values like "Editor" or "Test"

2. **"Template not found" error**
   - Check available templates with: `./repo.sh template list`
   - Ensure template name is spelled correctly

3. **"File already exists" error**
   - Clean up existing files: `rm -rf source/apps/your_app.kit`
   - Or choose a different name

4. **Build failures after generation**
   - Run validation: `python3 tools/repoman/template_validator.py test-all`
   - Check for missing dependencies
   - Ensure all extensions are properly configured

### Debug Mode

Enable verbose output for debugging:

```bash
# Verbose template generation
bash -x ./repo.sh template new kit_base_editor --name=test.app

# Debug Python engine directly
python3 tools/repoman/template_engine.py kit_base_editor --name=test.app --version=1.0.0
```

## Architecture

### Components

1. **Template Engine** (`tools/repoman/template_engine.py`)
   - Handles configuration loading and merging
   - Performs variable interpolation
   - Generates playback files for template replay

2. **Configuration Manager**
   - Loads TOML configuration files
   - Handles inheritance via `includes`
   - Manages variable resolution

3. **Template Validator** (`tools/repoman/template_validator.py`)
   - Validates configurations
   - Checks generated files
   - Runs comprehensive test suites

4. **Repository Shell Script** (`repo.sh`)
   - Entry point for template operations
   - Handles argument parsing
   - Invokes Python engine

### Data Flow

```
User Input → repo.sh → Template Engine → Configuration Manager
                             ↓
                     Template Generation
                             ↓
                        Validation
                             ↓
                      Generated Files
```

## Contributing

### Adding New Templates

1. Create template directory structure
2. Add entry to `templates/templates.toml`
3. Define default variables
4. Add validation tests
5. Update documentation

### Extending Configuration System

1. Add new configuration schemas
2. Implement custom validators
3. Add interpolation functions
4. Create inheritance rules

## Support

For issues or questions:
- Check this documentation
- Run validation tests
- Review example configurations
- Submit issues to the repository